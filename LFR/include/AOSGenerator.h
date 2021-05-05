/* Copyright 2013 Simon Opelt and Clemens Birklbauer. All rights reserved.
 * For license and copyright information see license.txt of LFC2013.
 */
#pragma once

#include <string>
#include <vector>
#include <glm/glm.hpp>


// predeclaration
class AOS;

class AOSGenerator // Universal & Unstructured LF Generator: takes care of loading the light field
{
private:

public:
	AOSGenerator(void);
	virtual ~AOSGenerator(void);
	void Generate( AOS *aos, const std::string &jsonPoseFile, const std::string &imgFilePath = "", const bool replaceExtension = false );
};


