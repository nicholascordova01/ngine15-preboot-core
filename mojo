# engine18_core_v1.2.mojo
# High-performance computational core for Chloe/Engine18.
# Copyright (c) 2025 Nicholas Cordova & GRUS.
# Corrected and optimized based on your final review.

from python import Python
from memory import DType, DTypePointer, memset_zero
from random import rand

# A struct for handling matrices
struct Matrix:
    var data: DTypePointer[DType.float32]
    var rows: Int
    var cols: Int

    fn __init__(inout self, rows: Int, cols: Int, initialize: Bool = false):
        let size = rows * cols
        self.data = DTypePointer[DType.float32].alloc(size)
        self.rows = rows
        self.cols = cols
        
        if initialize:
            # Fill with non-zero values for meaningful tests
            for i in range(size):
                # Correction: Use native Float32 type for rand specialization
                self.data.store(i, rand[Float32]())
        else:
            memset_zero(self.data, size)

    fn __del__(inout self):
        self.data.free()

    fn get(self, row: Int, col: Int) -> Float32:
        return self.data.load(row * self.cols + col)

    fn set(self, row: Int, col: Int, val: Float32):
        self.data.store(row * self.cols + col, val)

# This is the Python-callable entry point
@python.object
class SVCF_Simulator:
    var matrix_a: Matrix
    var matrix_b: Matrix
    var result_matrix: Matrix

    # Correction: Use Mojo's `true`/`false` literals
    fn __init__(self, size: Int):
        self.matrix_a = Matrix(size, size, initialize=true)
        self.matrix_b = Matrix(size, size, initialize=true)
        self.result_matrix = Matrix(size, size)
        print("[Mojo Core] SVCF Simulator Initialized.")

    # High-performance matrix multiplication implemented in Mojo
    fn run_svcf_step(self):
        print("[Mojo Core] Running one step of SVCF simulation...")
        for i in range(self.matrix_a.rows):
            for j in range(self.matrix_b.cols):
                var sum: Float32 = 0.0
                for k in range(self.matrix_a.cols):
                    sum += self.matrix_a.get(i, k) * self.matrix_b.get(k, j)
                self.result_matrix.set(i, j, sum)
        print("[Mojo Core] SVCF step complete.")

    # Converts Mojo data back to a Python object
    fn get_result_as_py(self) -> Python.Object:
        np = Python.import_module("numpy")
        
        py_list = []
        for i in range(self.result_matrix.rows):
            row = []
            for j in range(self.result_matrix.cols):
                row.append(self.result_matrix.get(i, j))
            py_list.append(row)
            
        return np.array(py_list)

# Main function to allow this file to be run for testing
fn main():
    print("--- Testing Engine18 Mojo Core v1.2 ---")
    let sim = SVCF_Simulator(4)
    sim.run_svcf_step()
    
    let result_np = sim.get_result_as_py()
    
    print("Result from Mojo, returned as NumPy array:")
    let py = Python.import_module("builtins")
    py.print(result_np)