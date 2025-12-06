OF_GLSL_SHADER_HEADER

in vec3 FragPos;
in vec3 Normal;

uniform bool useAlbedo;  
//textures
uniform sampler2D texA;
uniform sampler2D texB;
in vec2 vUv;
uniform float split;
uniform vec2 screenSize;

//normal maps
uniform bool useNormalMap;
uniform sampler2D normalMapA;
uniform sampler2D normalMapB;

uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;
uniform vec3 objectColor;

out vec4 fragColor;

void main()
{
    // screen split (0 = left, 1 = right)
    float screenX = gl_FragCoord.x / screenSize.x;
    float side    = step(split, screenX);

    // Start with the interpolated normal as fallback
    vec3 N = normalize(Normal);

    if (useNormalMap) {
        // sample both normal maps
        vec3 nA = texture(normalMapA, vUv).rgb;
        vec3 nB = texture(normalMapB, vUv).rgb;

        // choose which one based on split
        vec3 nTex = mix(nA, nB, side);

        // convert from [0,1] RGB to [-1,1] normal and normalize
        nTex = nTex * 2.0 - 1.0;
        N = normalize(nTex);
    }

    // ----- LIGHTING -----

    // Ambient
    float ambientStrength = 0.8;
    float ambient = ambientStrength;

    // Diffuse
    vec3 L = normalize(lightPos - FragPos);
    float diffuse = max(dot(N, L), 0.0);

    // Specular
    float specularStrength = 0.5;
    vec3 V = normalize(viewPos - FragPos);
    vec3 R = normalize(-L + 2.0 * N * dot(L, N));
    float spec = pow(max(dot(V, R), 0.0), 32.0);
    float specular = specularStrength * spec;

    // ----- ALBEDO (color textures) -----
    vec3 albedo = vec3(1.0);

    if (useAlbedo) {
        vec3 a = texture(texA, vUv).rgb;
        vec3 b = texture(texB, vUv).rgb;
        albedo = mix(a, b, side);
    }

    // ----- FINAL COLOR -----
    vec3 result = (ambient + diffuse + specular) * (objectColor * albedo);
    fragColor = vec4(result, 1.0);
    //fragColor = vec4(vec3(diffuse), 1.0);
}
