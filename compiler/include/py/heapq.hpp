#ifndef HEAPQ_HPP
#define HEAPQ_HPP

#include <cstdlib>
#include <algorithm>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>


namespace py = pybind11;

namespace pydd {

  /*
    Note:
    We need min heap for ipnsw while std::make_heap is max heap.
    So, key is multiplied by -1 to support min heap...
   */
  // class Heap {
  // public:
  //   Heap() {
  //     this->_heap_data.clear(); 
  //   }
  //   Heap(float key, int data) {
  //     this->_heap_data.clear(); 
  //     this->_heap_data.push_back(std::make_pair(-key, data)); 
  //     std::make_heap(this->_heap_data.begin(), this->_heap_data.end());
  //   }

  //   void push(float key, int data) {
  //     this->_heap_data.push_back(std::make_pair(-key, data)); 
  //     std::push_heap(this->_heap_data.begin(), this->_heap_data.end());
  //   }

  //   std::pair<float, int> pop() {
  //     std::pop_heap(this->_heap_data.begin(), this->_heap_data.end()); 
  //     std::pair<float, int> res = this->_heap_data.back();
  //     this->_heap_data.pop_back();
  //     res.first = -res.first;
  //     return res; 
  //   }

  //   float peek() {
  //     return - (this->_heap_data.front().first);
  //   }

  //   int get_size() { return _heap_data.size(); }
  // private:
  //   int _size; 
  //   std::vector<std::pair<float, int>> _heap_data; 
  // }; 

  // Heap heapinit(float key, int data) {
  //   return Heap(key, data); 
  // }

  // void heappush(Heap &tgt_heap, float key, int data) {
  //   tgt_heap.push(key, data); 
  // }

  // std::vector<float> *heappop(Heap &tgt_heap) {
  //   std::pair<float, int> res_pair = tgt_heap.pop();
  //   std::vector<float> *res = new std::vector<float>{res_pair.first, (float)res_pair.second};
  //   return res; 
  // }

  // float heappeek(Heap &tgt_heap) {
  // 	return tgt_heap.peek(); 
  // }

  // int heapsize(Heap &tgt_heap) {
  // 	return tgt_heap.get_size(); 
  // }

  template <typename K, typename V>
  class Heap {
  
  private:
    int _size;
    std::vector<std::pair<K, V>> _heap_data;

  public:

    Heap() {
      this->_heap_data.clear(); 
    }

    Heap(K key, V data) {
      this->_heap_data.clear(); 
      this->_heap_data.push_back(std::make_pair(-key, data)); 
      std::make_heap(this->_heap_data.begin(), this->_heap_data.end());
    }

    void push(K key, V data) {
      this->_heap_data.push_back(std::make_pair(-key, data)); 
      std::push_heap(this->_heap_data.begin(), this->_heap_data.end());
    }

    std::pair<K, V> pop() {
      std::pop_heap(this->_heap_data.begin(), this->_heap_data.end()); 
      std::pair<float, int> res = this->_heap_data.back();
      this->_heap_data.pop_back();
      res.first = -res.first;
      return res; 
    }

    K peek() {
      return - (this->_heap_data.front().first);
    }

    int get_size() { return _heap_data.size(); }

    std::vector<std::pair<K, V>>& heap_data() { return _heap_data; }

  }; 

  template <typename K, typename V>
  Heap<K, V> heapinit(K key, V data) {
    return Heap<K, V>(key, data);
  }

  template <typename K=int, typename V=int>
  Heap<K, V> heapinit_empty() {
    return Heap<K, V>();
  }


  template <typename K, typename V>
  void heappush(Heap<K, V> &tgt_heap, K key, V data) {
    tgt_heap.push(key, data); 
  }

  template <typename K, typename V>
  std::vector<K> *heappop(Heap<K, V> &tgt_heap) {
    std::pair<K, V> res_pair = tgt_heap.pop();
    std::vector<K> *res = new std::vector<K>{res_pair.first, (K) res_pair.second};
    return res;
  }

  template <typename K, typename V>
  void heappop1(Heap<K, V> &tgt_heap) {
    tgt_heap.pop();    
  }

  template <typename K, typename V>
  float heappeek(Heap<K, V> &tgt_heap) {
  	return tgt_heap.peek(); 
  }

  template <typename K, typename V>
  int heapsize(Heap<K, V> &tgt_heap) {
  	return tgt_heap.get_size(); 
  }

  template <typename K, typename V>
  int len(Heap<K, V> &tgt_heap) {
  	return tgt_heap.get_size(); 
  }

  template <typename K, typename V>
  K getitem(Heap<K, V> &tgt_heap, int i) {
  	return tgt_heap.heap_data()[i]; 
  }

  template <typename K, typename V>
  K heap_get_key(Heap<K, V> &tgt_heap, int i) {
  	return (- tgt_heap.heap_data()[i].first); 
  }
}


#endif // HEAPQ_HPP
