OF_GLSL_SHADER_HEADER

in vec3 FragPos;
in vec3 Normal;

uniform bool useAlbedo;  
uniform sampler2D texA;
uniform sampler2D texB;
in vec2 vUv;
uniform float split;
uniform vec2 screenSize;


uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;
uniform vec3 objectColor;

out vec4 fragColor;

void main()
{

    // Ambient
    float ambientStrength = 0.1;
    float ambient = ambientStrength;

    // Diffuse
    vec3 N = normalize(Normal); // interpolation might give something that isn't unit length
    vec3 L = normalize(lightPos - FragPos);
    float diffuse = max(dot(N, L), 0.0);
    

    // Specular
    float specularStrength = 0.5;
    vec3 V = normalize(viewPos - FragPos);
//    vec3 R = reflect(-L, N);
	vec3 R = normalize(-L + 2.0*N*dot(L,N));
    float spec = pow(max(dot(V, R), 0.0), 32);
    float specular = specularStrength * spec;
	//specular = 0;

   // vec3 result = (ambient + diffuse + specular) * objectColor;
  //  fragColor = vec4(result.rgb, 1.0);

  


    //vec3 albedo = useAlbedo ? texture(texB, vUv).rgb : vec3(1.0);

    vec3 albedo = vec3(1.0);

    if(useAlbedo){
        //0 to 1 representation of pixels x-coordinate on the screen - 0 all the way left and 1 all the way right
        float screenX = gl_FragCoord.x / screenSize.x;
        
        //check which side the pixel is on and which texture to use
        float side = step(split, screenX);
        
        vec3 a = texture(texA,vUv).rgb;
        vec3 b = texture(texB,vUv).rgb;
        albedo = mix(a,b,side);
    }

    vec3 result = (ambient +diffuse +specular) * (objectColor * albedo);
    fragColor = vec4(result.rgb,1.0);

  //  fragColor.rgb = vec3(N.x*0.5+0.5, 0.3, N.z*0.5+0.5);

   // fragColor = vec4(0.7,0.3,0.1,1.0); // test with constant color
}

