#version 330 compatibility
out vec2 texcoord;

#define GEOMETRY_SHADERS

void main() {
    texcoord = gl_MultiTexCoord0.xy;
    gl_Position = ftransform();

#ifdef GEOMETRY_SHADERS
    /* 只有打开宏时才走 GS 路径，没有独立 .gsh 文件 */
    gl_Position = gl_in[0].gl_Position;
    EmitVertex();
    EndPrimitive();
#endif
}
