#include "ofApp.h"

//--------------------------------------------------------------
void ofApp::setup(){
	ofEnableDepthTest();
	ofEnableLighting();

	light.setup();

	light.setPosition(0, 5000, 0);
	light.setDiffuseColor(ofFloatColor(1.0, 1.0, 1.0));
	light.setSpecularColor(ofFloatColor(1.0, 1.0, 1.0));
	light.setAmbientColor(ofFloatColor(0.1, 0.1, 0.1));
	//light.setOrientation(glm::vec3(45, 45, 0));

	kitchenModel.loadModel("kitchen.obj");
	
	bool ok = chairModel.loadModel("chair.obj");
	if (!ok) {
		printf("Error loading model\n");
	}
	else {
		printf("Model loaded. Mesh count: %d\n", (int)chairModel.getMeshCount());
	}

	//chairModel.loadModel("chair.obj");


	cam.setDistance(2000);
	cam.setFarClip(20000.f);
	cam.setPosition(0, 1000, 7000);
	cam.lookAt(glm::vec3(0, 0, 0));

	int centerX = ofGetWidth() * 0.5;
	int centerY = ofGetHeight() * 0.5;

	//model.setPosition(centerX, centerY + 100, 200);
	kitchenModel.setPosition(0, 0, 0);
	kitchenModel.setScale(10.0, 10.0, 10.0);

	kitchenModel.setRotation(0, 180, 0, 1, 0); // rotate 180° around Y
	kitchenModel.setRotation(1, 180, 0, 0, 1); // then 180° around Z

	chairModel.setPosition(0, 0, 0);
	chairModel.setScale(10.0, 10.0, 10.0);

	chairModel.setRotation(0, 180, 0, 1, 0); // rotate 180° around Y
	chairModel.setRotation(1, 180, 0, 0, 1); // then 180° around Z


	//orreryBase.setPosition(centerX, centerY + 100, 200);

	
}

//--------------------------------------------------------------
void ofApp::update(){

}

//--------------------------------------------------------------
void ofApp::draw(){
	light.enable();
	cam.begin();
	if (currentModel == 0) {
		kitchenModel.drawFaces();
	}
	else {
		//chairModel.drawFaces();
		//ofDisableLighting();
		//ofSetColor(255);
		chairAngle += 1.0f;
		//chairModel.setRotation(0, chairAngle, 0, 1, 0);
		//chairModel.rotateDeg(0, 0, 1, 0);
		chairModel.drawFaces();   // or chairModel.drawFaces();
		//ofEnableLighting();
	}

	//orreryBase.draw();
	cam.end();
	light.disable();
}



//--------------------------------------------------------------
void ofApp::keyPressed(int key){
	if (key == '1') {
		currentModel = 0;
	}
	else if (key == '2') {
		currentModel = 1;
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
