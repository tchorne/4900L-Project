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
	kitchenModel.loadModel("kitchen.obj");
	chairModel.loadModel("chair.obj");

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

	//temp object to display a cylinder at light position for tracking
	cylLighting.setResolution(10, 16, 2);
	cylLighting.setHeight(200);

	//earth texture
	ofDisableArbTex();
	//ofLoadImage(earth, "1_earth_8k.jpg");
	bool ok = ofLoadImage(earth, "1_earth_8k.jpg");

	if (!ok) {
		ofLogError() << "Failed to load earth texture!";
	}
	else {
		ofLogNotice() << "Loaded earth texture: "
			<< earth.getWidth() << "x" << earth.getHeight();
	}

	//sphereEarth.mapTexCoordsFromTexture(earth);

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
	lightingShader.setUniform3f("lightColor", glm::vec3(1, 1, 1));
	lightingShader.setUniform3f("objectColor", glm::vec3(0.6, 0.6, 0.9));
	
	
	//to display temp lighting cylinder
	lightingShader.setUniformMatrix4f("worldMatrix", cylLighting.getGlobalTransformMatrix());
	cylLighting.setPosition(lightPos);
	cylLighting.draw();

	//if current model is kitchen
	if (currentModel == 1) {
		lightingShader.setUniformMatrix4f("worldMatrix", kitchenModel.getModelMatrix());
		lightingShader.setUniform1i("useAlbedo", false);
		//custom lighting only works if materials are disabled
		kitchenModel.disableMaterials();
		kitchenModel.drawFaces();

	}
	//else if current model is chair
	else if (currentModel ==2){
		lightingShader.setUniformMatrix4f("worldMatrix", chairModel.getModelMatrix());
		//custom lighting only works if materials are disabled
		chairModel.disableMaterials();
		chairModel.drawFaces();
	}
	else {
		
		lightingShader.setUniformMatrix4f("worldMatrix", sphereEarth.getGlobalTransformMatrix());

		//earth.bind();
		sphereEarth.rotate(0.1, 0, 1, 0);

		lightingShader.setUniform1i("useAlbedo", true);
		lightingShader.setUniformTexture("albedoTex", earth, 0);
		sphereEarth.draw();
		//earth.unbind();
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
	//for chair model
	else if (key == '2') {
		currentModel = 2;
	}
	else if (key == '3') {
		currentModel = 3;
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
