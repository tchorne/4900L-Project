OF_GLSL_SHADER_HEADER

// base vertex shader for lighting code

uniform mat4 modelViewProjectionMatrix;
uniform mat4 worldMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

in vec4 position;
in vec3 normal;

out vec3 FragPos;
out vec3 Normal; 

void main() {
    FragPos = vec3((worldMatrix * position).xyz); // position in world space
    Normal = normalize((worldMatrix * vec4(normal.xyz,0)).xyz); // normals in world space; note w=0
    gl_Position = projectionMatrix * viewMatrix * worldMatrix * position;
}
