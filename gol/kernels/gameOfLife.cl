__kernel void gameOfLifeStep(
    __global const uchar* src, 
    __global uchar* dst, 
    const int width, 
    const int height) 
{
    int x = get_global_id(0);
    int y = get_global_id(1);

    // Stay within bounds of the grid
    if (x >= width || y >= height) return;

    int neighbors = 0;

    // Check all 8 neighbors
    for (int dy = -1; dy <= 1; dy++) {
        for (int dx = -1; dx <= 1; dx++) {
            if (dx == 0 && dy == 0) continue;

            int nx = x + dx;
            int ny = y + dy;

            if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
                if (src[ny * width + nx] > 0) {
                    neighbors++;
                }
            }
        }
    }

    int current_idx = y * width + x;
    uchar is_alive = src[current_idx];

    // Standard Conway's Rules
    uchar next_state = 0;
    if (is_alive > 0) {
        next_state = (neighbors == 2 || neighbors == 3) ? 1 : 0;
    } else {
        next_state = (neighbors == 3) ? 1 : 0;
    }

    dst[current_idx] = next_state;
}