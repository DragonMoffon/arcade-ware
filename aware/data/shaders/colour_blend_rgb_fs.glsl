#version 330

in vec4 vs_colour;

out vec4 fs_colour;

void main(){
    fs_colour = vs_colour;
}