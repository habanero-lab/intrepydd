
#include "intrepydd_perf.hpp"

#include <cstring>
#include <iostream>

#define DEBUG

// Strings for the perf counters
std::map<int, std::string> pydd_perf::perf::hpm_strings = {
            {PAPI_TOT_CYC, "PAPI Total Cycles"},
            {PAPI_TOT_INS, "PAPI Total Instructions"}
        };


const double pydd_perf::perf::EnergyPerInstruction = 20e-12;
const double pydd_perf::perf::EnergyDRAMPerBit = 25e-12;


void pydd_perf::perf::init()
{
    this->EventSet = PAPI_NULL;
    this->counter_started = false; // counters have not started
    this->event_count = 0;

    this->hwinfo = PAPI_get_hardware_info();

    int retval = PAPI_library_init(PAPI_VER_CURRENT);
    if (retval != PAPI_VER_CURRENT) {
        std::cerr << "PAPI library init failure" << std::endl;
        std::exit(EXIT_FAILURE);
    }

    // Push back counters that we will need to read
    // this->hpm_counters.push_back(PAPI_TOT_CYC);
    // this->hpm_counters.push_back(PAPI_TOT_INS);

    // push LLC misses into native events counter
    this->native_events.push_back("ix86arch::LLC_MISSES"); // push LLC misses

    // Total instruction counter
    this->native_events.push_back("INST_RETIRED");
    this->native_events.push_back("FP_ARITH:SCALAR_DOUBLE");
    this->native_events.push_back("FP_ARITH:SCALAR_SINGLE");
    this->native_events.push_back("FP_ARITH:128B_PACKED_DOUBLE");
    this->native_events.push_back("FP_ARITH:128B_PACKED_SINGLE");
    this->native_events.push_back("FP_ARITH:256B_PACKED_DOUBLE");
    this->native_events.push_back("FP_ARITH:256B_PACKED_SINGLE");
    this->native_events.push_back("FP_ARITH:512B_PACKED_DOUBLE");
    this->native_events.push_back("FP_ARITH:512B_PACKED_SINGLE");


    // Create PAPI event set
    if ( (retval = PAPI_create_eventset(& (this->EventSet)) ) != PAPI_OK) {
        std::cerr << "Could not create PAPI event set: " << PAPI_strerror(retval) << std::endl;
    }

    // Add HPM counters
    for (auto hpm : this->hpm_counters) {
        // check total instruction counter
        if (PAPI_query_event(hpm) != PAPI_OK) {
            std::cerr << "Counter: " << this->hpm_strings[hpm] << " does not exist" << std::endl;
            std::exit(EXIT_FAILURE);
        }

        if (PAPI_get_event_info(hpm, &this->info) != PAPI_OK) {
            std::cerr << "Counter: " << this->hpm_strings[hpm] << " could not get info" << std::endl;
        } else {
            this->hpc_info[hpm] = this->info;
        }
    }

    // Register counters to the event set
    for (auto hpm : this->hpm_counters) {
        if ( (retval = PAPI_add_event(this->EventSet, hpm)) != PAPI_OK) {
            std::cerr << "Event Set: Could not add " << this->hpm_strings[hpm] << ": " << PAPI_strerror(retval) << std::endl;
        } else {
            this->hpc_values[hpm] = 0; // setup counter to 0
            this->event_count++;
        }
    }

    // Add native events
    for (int i = 0; i < native_events.size(); i++) {
        retval = PAPI_add_named_event(this->EventSet, native_events[i].c_str());
        if (retval != PAPI_OK) {
            std::cerr << "Could not add native event : " << native_events[i].c_str() << std::endl;
        } else {
            this->native_events_actual.push_back(native_events[i]); // actual events that are tracked
            this->native_values[native_events[i]] = 0;
            this->event_count++;
        }
    }


    std::cout << "Perf has been initialized" << std::endl;
}

void pydd_perf::perf::reset()
{
    // reset all counters and native events to 0
    for (auto hpm_val = this->hpc_values.begin(); hpm_val != this->hpc_values.end(); hpm_val++) {
        hpm_val->second = 0;
    }

    for (auto native_val = this->native_values.begin(); native_val != this->native_values.end(); native_val++) {
        native_val->second = 0;
    }

    this->counter_started = false;

    this->cycles_after = this->cycles_before = 0;
    this->time_after = this->time_before = 0;
}

void pydd_perf::perf::start_timing()
{

    if (this->counter_started) {
        std::cerr << "Counter reading already active" << std::endl;
        return;
    }

    // Start reading PAPI counters
    if (PAPI_start(this->EventSet) != PAPI_OK) {
        std::cerr << "Could not start timing event" << std::endl;
    } else {
        this->counter_started = true;
    }

    // Timing and cycles before
    this->cycles_before = PAPI_get_real_cyc();
    this->time_before = PAPI_get_real_usec();
}

void pydd_perf::perf::stop_timing()
{
    if (this->counter_started == false) {
       std::cerr << "Counters have not been started yet" << std::endl;
       return;
    }

    // Fall back time option reading
    this->time_after = PAPI_get_real_usec();
    this->cycles_after = PAPI_get_real_cyc();

    // temp array for reading values
    long long values[ this->native_events_actual.size() ];
    std::memset(values, 0, sizeof(long long) * this->native_events_actual.size());

    // stop counters and accumulate values into the counters map
    if (PAPI_stop(this->EventSet, values) != PAPI_OK) {
        std::cerr << "Could not stop and reading timing counters" << std::endl;
    } else {

        for (auto i = 0u; i < this->native_events_actual.size(); i++) {
            this->native_values[this->native_events_actual[i]] += values[i];
        }

        this->counter_started = false;
    }

}

double pydd_perf::perf::compute_metric()
{
    // Time computation as a fall back option
    long long real_time = (this->time_after - this->time_before); // micro seconds
    long long cycle_time = this->cycles_after - this->cycles_before; // total cycles

    long long total_inst = this->native_values["INST_RETIRED"];

    if (this->native_values.find("FP_ARITH:SCALAR_DOUBLE") != this->native_values.end()) {
        total_inst += this->native_values["FP_ARITH:SCALAR_DOUBLE"];
    }
    if (this->native_values.find("FP_ARITH:SCALAR_DOUBLE") != this->native_values.end()) {
        total_inst += this->native_values["FP_ARITH:SCALAR_DOUBLE"];
    }
    if (this->native_values.find("FP_ARITH:128B_PACKED_DOUBLE") != this->native_values.end()) {
        total_inst += 2 * this->native_values["FP_ARITH:128B_PACKED_DOUBLE"];
    }
    if (this->native_values.find("FP_ARITH:256B_PACKED_DOUBLE") != this->native_values.end()) {
        total_inst += 4 * this->native_values["FP_ARITH:256B_PACKED_DOUBLE"];
    }
    if (this->native_values.find("FP_ARITH:512B_PACKED_DOUBLE") != this->native_values.end()) {
        total_inst += 8 * this->native_values["FP_ARITH:512B_PACKED_DOUBLE"];
    }
    if (this->native_values.find("FP_ARITH:128B_PACKED_SINGLE") != this->native_values.end()) {
        total_inst += 4 * this->native_values["FP_ARITH:512B_PACKED_SINGLE"];
    }
    if (this->native_values.find("FP_ARITH:256B_PACKED_SINGLE") != this->native_values.end()) {
        total_inst += 8 * this->native_values["FP_ARITH:256B_PACKED_SINGLE"];
    }
    if (this->native_values.find("FP_ARITH:512B_PACKED_SINGLE") != this->native_values.end()) {
        total_inst += 16 * this->native_values["FP_ARITH:512B_PACKED_SINGLE"];
    }

    double inst_energy = this->EnergyPerInstruction * (double) total_inst;

    // memory energy is defined as energyPerBit * number of misses * sizeof 1 block
    double mem_energy = this->EnergyDRAMPerBit * (double) this->native_values["ix86arch::LLC_MISSES"] * (64.0 * 8.0);

    double total_energy = mem_energy + inst_energy;

    // Note : total time is converted to seconds
    double total_time = real_time / 1e6; // We can adjust this later for a more refined answer

    #ifdef DEBUG
        for (auto nc : this->native_values) {
            std::cerr << nc.first << ": " << nc.second << std::endl;
        }
        std::cerr << "Total Inst: " << total_inst << std::endl;
        std::cerr << "E: " << total_energy << std::endl;
        std::cerr << "D: " << total_time << std::endl;
        std::cerr << "ED^2P: " << total_energy * (total_time * total_time) << std::endl;
    #endif

    return total_energy * (total_time * total_time); // Return ED^2P
}
