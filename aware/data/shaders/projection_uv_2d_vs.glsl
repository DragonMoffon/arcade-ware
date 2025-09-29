#version 330

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

in vec4 in_coordinate;
in vec4 in_colour

out vec2 vs_uv;
out vec4 vs_colour

void main(){
    gl_Position = window.projection * window.view * vec4(in_coordinate.xy, 0.0, 1.0);
    vs_uv = in_coordinate.zw;
    vs_colour = in_colour;
}