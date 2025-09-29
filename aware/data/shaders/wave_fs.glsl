#version 330

#define TAU 6.28318530718

in vec2 vs_uv;
in vec4 vs_colour;

uniform vec4 wave;
uniform int blend;

out vec4 fs_colour;

void main(){
    float x = vs_uv.x;
    float t = wave.w;

    float offset = wave.x * 0.5 * (sin(TAU * (x / wave.y - t / wave.z)) + 1);
    if (vs_uv.y < (offset - blend)) discard;
    fs_colour = vs_colour;
 
    // anti-aliasing
    if (blend > 0) fs_colour.a = vs_colour.a * clamp((vs_uv.y - offset + blend) / blend, 0.0, 1.0);
}