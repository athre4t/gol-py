import os
import numpy as np
import pyopencl as cl
from .engine import GameOfLifeEngine

class GameOfLifeGpu(GameOfLifeEngine):
    def __init__(self):
        super().__init__("GPU (OpenCL)")
        self.ctx = None
        self.queue = None
        self.knl_step = None
        self.src_buf = None
        self.dst_buf = None

    def _init_gpu(self, width, height):
        platforms = cl.get_platforms()
        device = next((d for p in platforms for d in p.get_devices(cl.device_type.GPU)), 
                      platforms[0].get_devices()[0])
        self.ctx = cl.Context([device])
        self.queue = cl.CommandQueue(self.ctx)
        
        kernel_path = os.path.join(os.path.dirname(__file__), '..', 'kernels', 'gameOfLife.cl')
        with open(kernel_path, 'r') as f:
            self.program = cl.Program(self.ctx, f.read()).build()
        self.knl_step = cl.Kernel(self.program, 'gameOfLifeStep')
        
        self.src_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, width * height)
        self.dst_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE, width * height)

    def simulate(self, grid, steps, visual_interval=None):
        if not self.ctx:
            self._init_gpu(grid.width, grid.height)
        host_data = np.ascontiguousarray(grid.current, dtype=np.uint8).ravel()
        cl.enqueue_copy(self.queue, self.src_buf, host_data)
        return super().simulate(grid, steps, visual_interval)

    def sync_to_host(self, grid):
        host_data = np.empty(grid.height * grid.width, dtype=np.uint8)
        cl.enqueue_copy(self.queue, host_data, self.src_buf)
        self.queue.finish()
        grid.current[:] = host_data.reshape(grid.height, grid.width).astype(bool)

    def step(self, grid):
        global_size = (((grid.width + 15) // 16) * 16, ((grid.height + 15) // 16) * 16)
        self.knl_step(self.queue, global_size, (16, 16), self.src_buf, self.dst_buf, 
                      np.int32(grid.width), np.int32(grid.height))
        self.src_buf, self.dst_buf = self.dst_buf, self.src_buf

    def cleanup(self):
        if self.src_buf:
            self.src_buf.release()
        if self.dst_buf:
            self.dst_buf.release()
        self.ctx = None