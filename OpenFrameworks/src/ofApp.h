#pragma once

#include "ofMain.h"
#include "ofxAssimpModelLoader.h"

class ofApp : public ofBaseApp{

	public:
		void setup();
		void update();
		void draw();

		void keyPressed(int key);
		void keyReleased(int key);
		void mouseMoved(int x, int y );
		void mouseDragged(int x, int y, int button);
		void mousePressed(int x, int y, int button);
		void mouseReleased(int x, int y, int button);
		void mouseEntered(int x, int y);
		void mouseExited(int x, int y);
		void windowResized(int w, int h);
		void dragEvent(ofDragInfo dragInfo);
		void gotMessage(ofMessage msg);

		//ofLight light;

		ofxAssimpModelLoader kitchenModel;
		ofxAssimpModelLoader chairModel;

		ofEasyCam cam;

		//keep track of current model
		int currentModel = 0;


		ofShader lightingShader;

		//temp cylinder for lighting testing
		ofCylinderPrimitive cylLighting;

		//light position for shader
		glm::vec3 lightPos;

};
