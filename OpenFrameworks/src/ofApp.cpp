#include "ofApp.h"


//--------------------------------------------------------------
void ofApp::setup(){
	ofEnableDepthTest();

	//load lighting shader
	lightingShader.load("shader/lighting");

	if (!lightingShader.isLoaded()) {
		printf("Shader didnt load.");
		ofLogError() << "Shader failed to load!";
		ofExit();
	}
	else {
		printf("Shader loaded.");
	}

	//load models
	//kitchenModel.loadModel("kitchen.obj");
	//chairModel.loadModel("chair.obj");
	//cowModel.loadModel("cowModel.obj");
	//loadModel("bunnyModel.obj");
	dragonModel.loadModel("dragonModel.obj");

	//setting up the lighting position 
	lightPos = glm::vec3(-500, 3000, 1000);

	//setting up the camera
	cam.setDistance(2000);
	cam.setFarClip(20000.f);
	cam.setPosition(0, 1000, 7000);
	cam.lookAt(glm::vec3(0, 0, 0));

	//center of the display
	int centerX = ofGetWidth() * 0.5;
	int centerY = ofGetHeight() * 0.5;

	//setting the position of the kitchen model to be centered in front of the camera
	kitchenModel.setPosition(0, 0, 0);
	kitchenModel.setScale(10.0, 10.0, 10.0);
	kitchenModel.setRotation(0, 180, 0, 1, 0); // rotate 180° around Y
	kitchenModel.setRotation(1, 180, 0, 0, 1); // then 180° around Z

	//setting the position of the chair model to be centered in front of the camera
	chairModel.setPosition(0, 0, 0);
	chairModel.setScale(10.0, 10.0, 10.0);
	chairModel.setRotation(0, 180, 0, 1, 0); // rotate 180° around Y
	chairModel.setRotation(1, 180, 0, 0, 1); // then 180° around Z

	//setting the position of the cow model to be centered in front of the camera
	cowModel.setPosition(0, 0, 0);
	cowModel.setScale(8.0, 8.0, 8.0);
	cowModel.setRotation(0, 180, 0, 1, 0); // rotate 180° around Y
	cowModel.setRotation(1, 180, 0, 0, 1); // then 180° around Z

	//setting the position of the bunny model to be centered in front of the camera
	bunnyModel.setPosition(0, 0, 0);
	bunnyModel.setScale(8.0, 8.0, 8.0);
	bunnyModel.setRotation(0, 180, 0, 1, 0); // rotate 180° around Y
	bunnyModel.setRotation(1, 180, 0, 0, 1); // then 180° around Z

	//setting the position of the bunny model to be centered in front of the camera
	dragonModel.setPosition(0, 0, 0);
	dragonModel.setScale(8.0, 8.0, 8.0);
	dragonModel.setRotation(0, 180, 0, 1, 0); // rotate 180° around Y
	dragonModel.setRotation(1, 180, 0, 0, 1); // then 180° around Z

	//temp object to display a cylinder at light position for tracking
	cylLighting.setResolution(10, 16, 2);
	cylLighting.setHeight(200);

	//earth texture
	ofDisableArbTex();
	ofLoadImage(earth, "earth_albedo.jpg");
	ofLoadImage(earthTexturePainted, "earth_albedo_painted.png");
	//earth normals
	ofLoadImage(earthNormals, "earth_normals.png");
	ofLoadImage(earthNormalsPainted, "earth_normals_SLIC.png");

	//load cow texture
	//ofLoadImage(cowTexture, "cow_albedo.png");
	//ofLoadImage(cowTexturePainted, "cow_albedo_painted.png");

	//load bunny texture
	//ofLoadImage(bunnyTexture, "bunny_albedo.png");
	//ofLoadImage(bunnyTexturePainted, "bunny_albedo_painted.png");

	//load dragon texture
	ofLoadImage(dragonTexture, "dragon_albedo.png");
	ofLoadImage(dragonTexturePainted, "dragon_albedo_painted.png");
	//dragon normals
	ofLoadImage(dragonNormals, "dragon_normals.png");
	ofLoadImage(dragonNormalsPainted, "dragon_normals_SLIC.png");

	sphereEarth.setPosition(0, 0, 0);
	sphereEarth.set(2000, 16);

}

//--------------------------------------------------------------
void ofApp::update(){

}

//--------------------------------------------------------------
void ofApp::draw(){

	ofDisableLighting();
	
	cam.begin();

	//setting up shader and passing in matrices
	lightingShader.begin();
	lightingShader.setUniformMatrix4f("viewMatrix", cam.getModelViewMatrix());
	lightingShader.setUniformMatrix4f("projectionMatrix", cam.getProjectionMatrix());
	lightingShader.setUniformMatrix4f("modelViewProjectionMatrix", cam.getModelViewProjectionMatrix());
	lightingShader.setUniform3f("viewPos", cam.getPosition());

	lightingShader.setUniform3f("lightPos", lightPos);
	lightingShader.setUniform3f("lightColor", glm::vec3(3, 3, 3));
	lightingShader.setUniform3f("objectColor", glm::vec3(0.6, 0.6, 0.9));
	
	
	//to display temp lighting cylinder
	lightingShader.setUniformMatrix4f("worldMatrix", cylLighting.getGlobalTransformMatrix());
	
	//draws a cylinder at light position
	//cylLighting.setPosition(lightPos);
	//cylLighting.setPosition(lightPos.x, lightPos.y +mouseY, lightPos.z);
	//cylLighting.draw();

	//if current model is kitchen
	
	//else if current model is dragon
	if (currentModel == 1) {
		lightingShader.setUniformMatrix4f("worldMatrix", dragonModel.getModelMatrix());

		float split = ofMap(mouseX, 0, ofGetWidth(), 0.0f, 1.0f, true);
		lightingShader.setUniform1f("split", split);

		lightingShader.setUniform2f("screenSize", (float)ofGetWidth(), (float)ofGetHeight());

		lightingShader.setUniform1i("useAlbedo", true);
		lightingShader.setUniformTexture("texA", dragonTexture, 0);
		lightingShader.setUniformTexture("texB", dragonTexturePainted, 1);
		lightingShader.setUniform1i("useNormalMap", 1);
		lightingShader.setUniformTexture("normalMapA", dragonNormals, 2);
		lightingShader.setUniformTexture("normalMapB", dragonNormalsPainted, 3);

		dragonModel.disableMaterials();


		dragonModel.drawFaces();
	}
	else {
		//if no model selected, draw the earth sphere
		lightingShader.setUniformMatrix4f("worldMatrix", sphereEarth.getGlobalTransformMatrix());

		sphereEarth.rotate(0.1, 0, 1, 0);

		//take mouse X position and split between two textures
		float split = ofMap(mouseX, 0, ofGetWidth(), 0.0f, 1.0f, true);
		lightingShader.setUniform1f("split", split);

		lightingShader.setUniform2f("screenSize",(float)ofGetWidth(),(float)ofGetHeight());

		lightingShader.setUniform1i("useAlbedo", true);
		lightingShader.setUniformTexture("texA", earth, 0);
		lightingShader.setUniformTexture("texB", earthTexturePainted, 1);
		lightingShader.setUniform1i("useNormalMap", 1);
		lightingShader.setUniformTexture("normalMapA", earthNormals, 2);
		lightingShader.setUniformTexture("normalMapB", earthNormalsPainted, 3);
		sphereEarth.draw();
	}

	lightingShader.end();

	cam.end();


	
}



//--------------------------------------------------------------
void ofApp::keyPressed(int key){
	//for kitchen model
	if (key == '1') {
		currentModel = 1;
	}
	//else earth model
	else {
		currentModel = 0;
	}
}

//--------------------------------------------------------------
void ofApp::keyReleased(int key){

}

//--------------------------------------------------------------
void ofApp::mouseMoved(int x, int y ){

}

//--------------------------------------------------------------
void ofApp::mouseDragged(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::mousePressed(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::mouseReleased(int x, int y, int button){

}

//--------------------------------------------------------------
void ofApp::mouseEntered(int x, int y){

}

//--------------------------------------------------------------
void ofApp::mouseExited(int x, int y){

}

//--------------------------------------------------------------
void ofApp::windowResized(int w, int h){

}

//--------------------------------------------------------------
void ofApp::gotMessage(ofMessage msg){

}

//--------------------------------------------------------------
void ofApp::dragEvent(ofDragInfo dragInfo){ 

}
