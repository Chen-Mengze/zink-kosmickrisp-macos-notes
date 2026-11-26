#version 430 compatibility
layout(local_size_x = 8, local_size_y = 8) in;

layout(std430, binding = 0) buffer LightData {
    vec4 lights[];
};

void main() {
    uint i = gl_GlobalInvocationID.x;
    lights[i] *= 0.5;
}
