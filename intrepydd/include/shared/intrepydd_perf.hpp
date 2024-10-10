
#include "papi.h"
#include <iostream>
#include <vector>
#include <map>

namespace pydd_perf {

    class perf {
        protected:

        // List of PAPI counters that will be read
        std::vector<int> hpm_counters;
        // Map from counters to collected values
        std::map<int, long long> hpc_values;
        // Map from counters to info structs
        std::map<int, PAPI_event_info_t> hpc_info;
        // Map from counters to strings
        static std::map<int, std::string> hpm_strings;

        // List of native event counters
        std::vector<std::string> native_events;
        std::vector<std::string> native_events_actual;
        std::map<std::string, long long> native_values;

        int EventSet;
        PAPI_event_info_t info;

        const PAPI_hw_info_t *hwinfo;


        // bool to check if reading counters have started
        bool counter_started;

        // even count
        int event_count;

        // Computed statistics
        double computed_energy;
        double computed_latency;
        double computed_ed2;

        // Time before and after
        long long time_before;
        long long time_after;
        long long cycles_before;
        long long cycles_after;

        // Constants
        static const double EnergyPerInstruction;
        static const double EnergyDRAMPerBit;

        public:
        perf() { } // For initializing our counters and trackers

        void init();
        void reset(); // Reset internal data structures
        void start_timing(); // Start collecting counters
        void stop_timing(); // Stop collecting counters
        double compute_metric(); // compute metrics from collected counters

    };
}

