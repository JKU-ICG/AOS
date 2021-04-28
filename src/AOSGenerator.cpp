
#include <glad/glad.h> // <-- try to get rid of it here!
#include "image.h"
#include "AOSGenerator.h"
#include "AOS.h"
#include "image.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <string>
#include <nlohmann/json.hpp> 
#include <glm/glm.hpp>
#include <glm/gtc/type_ptr.hpp>
//#include <FreeImage.h>

using namespace nlohmann; // for parsing JSON files


#define _USE_MATH_DEFINES
#include <cmath>

AOSGenerator::AOSGenerator(void)
{
}

AOSGenerator::~AOSGenerator(void)
{
}

glm::mat4 ParseMatrix(json::value_type jMat) // Matrice 3x4
{
	double data[16] = { 1,0,0,0,
						0,1,0,0,
						0,0,1,0,
						0,0,0,1 };
	assert(jMat.size() == 3);


	for (int ir = 0; ir < jMat.size(); ir++)
	{
		assert(jMat[ir].size() == 4);
		for (int ic = 0; ic < jMat[ir].size(); ic++)
		{
			if (jMat[ir][ic].is_string())
			{
				auto v = jMat[ir][ic].get<std::string>();
				data[ic * 4 + ir] = stod(v);
			}
			else if (jMat[ir][ic].is_number())
			{
				data[ic * 4 + ir] = jMat[ir][ic];
			}
			else
			{
				throw "unknown data type in matrix!";
			}
		}

	}


	return glm::make_mat4(data);

}

void AOSGenerator::Generate(AOS* aos, const std::string& jsonPoseFile, const std::string& imgFilePath, bool replaceExt)
{
	std::ifstream poseStream(jsonPoseFile);
	json j;
	poseStream >> j; // parse json
	poseStream.close();

	//std::cout << "images size: " << j["images"].size() << std::endl;
	if (j["images"].size() > 0)
	{
		//lf = new Lightfield(j["images"].size());
		auto jimg = j["images"];
		for (auto i = 0; i < jimg.size(); ++i) {
			auto m = ParseMatrix(jimg[i]["M3x4"]);

			std::string fname = (jimg[i]["imagefile"]);
			auto pose = m;

			std::string name = fname;
			if(replaceExt) name.replace(fname.find(".tiff"), strlen(".tiff"), ".png");
			Image img = load_image( (imgFilePath + "/" + name).c_str() );
			if( !is_empty_image(img) )
				aos->addView(img, pose, name);
			free_image(img);

			// DEBUG
			// std::cout << "imgfilename: " << jimg[i]["imagefile"] << std::endl;
			// std::cout << "matrix: " << jimg[i]["M3x4"] << std::endl;
			// auto translation = glm::vec3(glm::inverse(m)[3]);
			// std::cout << "translation: " << translation.x << ", " << translation.y << ", " << translation.z << "\n";
		}

	}

}

/*
glm::mat4 parseMatrix(ptree const& Mtree)
{
	matrix m; setIdentity(m.data); // 4 x 4 matrix
	auto rows = Mtree.size(); // rows
	int ir = 0, ic = 0; // counter for column and row

	for (auto& ritem : Mtree.get_child(""))
	{
		auto columns = ritem.second.size();
		ic = 0;
		for (auto& citem : ritem.second.get_child(""))
		{
			m.data[ic*4+ir] = citem.second.get_value<float>();
			++ic;
		}

		++ir;
	}

	// Matlab writes columns from left to right and OpenGL matrix convention is the same!
	/*	[ 0, 4, 8,12 ]
	[ 1, 5, 9,13 ]
	[ 2, 6,10,14 ]
	[ 3, 7,11,15 ]
	/

	return m;
}
*/

/*
// utility function for loading a 2D texture from file
// ---------------------------------------------------
unsigned int loadImageSTBI(const std::string path, const bool flip_vertically=false)
{
	unsigned int textureID = 0;
	

	int width, height, nrComponents;
	stbi_set_flip_vertically_on_load(flip_vertically); // tell stb_image.h to flip loaded texture's on the y-axis.
	unsigned char *data = stbi_load(path.c_str(), &width, &height, &nrComponents, 0);
	if (data)
	{
		assert(width > 0);
		assert(height > 0);
		assert(nrComponents > 0);

#ifndef NO_OPENGL
		glGenTextures(1, &textureID);

		GLenum format;
		if (nrComponents == 1)
			format = GL_RED;
		else if (nrComponents == 3)
			format = GL_RGB;
		else if (nrComponents == 4)
			format = GL_RGBA;

		glBindTexture(GL_TEXTURE_2D, textureID);
		glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, data);
		//glGenerateMipmap(GL_TEXTURE_2D); // <- not supported in OpenGL ES!

		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE ); // for this tutorial: use GL_CLAMP_TO_EDGE to prevent semi-transparent borders. Due to interpolation it takes texels from next repeat 
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE );
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR); // GL_LINEAR_MIPMAP_LINEAR <- not supported in OpenGL ES!
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
#endif

		stbi_image_free(data);
	}
	else
	{
		std::cout << "Texture failed to load at path: " << path << std::endl;
		stbi_image_free(data);
	}

	return textureID;
}
*/


/*
Lightfield *AOSGenerator::Generate(const std::string &jsonPoseFile, const std::string &imgFilePath)
{
	Lightfield *lf = 0;

	std::ifstream poseStream(jsonPoseFile);
	json j;
	poseStream >> j; // parse json
	poseStream.close();

	//std::cout << "images size: " << j["images"].size() << std::endl;
	if (j["images"].size() > 0)
	{
		lf = new Lightfield(j["images"].size());
		auto jimg = j["images"];
		for (auto i = 0; i < jimg.size(); ++i) {
			auto m = ParseMatrix(jimg[i]["M3x4"]);

			lf->names.push_back( jimg[i]["imagefile"] );
			lf->poses.push_back(m);

			// DEBUG
			// std::cout << "imgfilename: " << jimg[i]["imagefile"] << std::endl;
			// std::cout << "matrix: " << jimg[i]["M3x4"] << std::endl;
			// auto translation = glm::vec3(glm::inverse(m)[3]);
			// std::cout << "translation: " << translation.x << ", " << translation.y << ", " << translation.z << "\n";
		}

	}

	for (auto& fname : lf->names) // access by const reference
	{
		std::string name = fname;
		name.replace(fname.find(".tiff"), strlen(".tiff"), ".png");
		lf->ogl_textures.push_back(loadImageSTBI(imgFilePath + "/" + name));
	}


	return lf;
} 
*/

/* OLD stuff, below!
	
#ifdef _DEBUG
	{
		cudaError_t error = cudaGetLastError();
		if (error != cudaSuccess) {

			printf("ERROR: %s\n", cudaGetErrorString(error));
		}
	}
#endif

	bCUDAUM = useCUDAUnifiedMemory;
	bool onlyloadsingleimagedebug = false;//true;
	void* globalsdata = NULL;

	unsigned long long totalDataSize = 0;


	LightfieldPtr lightfield(new Lightfield());

	lightfield->pageWidthPx = options->GetPageWidthPx();
	lightfield->pageHeightPx = options->GetPageHeightPx();
	

	std::string base = options->GetDatasetBase();

	int cudaDevice = -1;
	cudaGetDevice(&cudaDevice);


	int pct = 0;
	int numCams = 0;
	bool grayscale = false, hasAlpha = false;
	ImageType itype;
	
	
	// Create an empty property tree object
	using boost::property_tree::ptree;
	ptree pt, imagestree;

	// Load the XML file into the property tree. If reading fails
	// (cannot open file, parse error), an exception is thrown.
	try
	{
		read_json(options->GetPosesFile(), pt);
		imagestree = pt.get_child("images");
	}
	catch (boost::exception &e)
	{
		std::cerr << boost::diagnostic_information_what(e);
		return lightfield;
	}

	numCams = imagestree.size();
	

	lightfield->dataCameras.resize(numCams);
	lightfield->resS = numCams;
	lightfield->resT = 1;
	lightfield->numCameras = numCams;

	std::cout << "loading " << numCams << " images ";

	boost::progress_display show_progress( numCams );

	auto imgTreeIter = imagestree.begin();
	int count = 0;
	while (imgTreeIter != imagestree.end())
	{
		

		int actualIndex = count;
		std::stringstream filename;
		FIBITMAP *image;
		filename << base;

		auto imgfile = imgTreeIter->second.get<std::string>("imagefile");

		filename << imgfile;

		FREE_IMAGE_FORMAT fif = FIF_UNKNOWN;
		fif = FreeImage_GetFileType(filename.str().c_str());
		image = FreeImage_Load(fif, filename.str().c_str());



		// error handling
		if (!image)
		{
			std::cout << "image '" << filename.str() << "' cannot be loaded !" << std::endl;
			exit(-1);
		}

		if (options->GetForceGrayscale())
		{
			FIBITMAP* tmpimg = image;
			image = FreeImage_ConvertToGreyscale(tmpimg);
			FreeImage_Unload(tmpimg);
		}

		if (!options->GetFlipImage())
		{
			FreeImage_FlipVertical(image);
		}


		// get image data and image settings (width, bpp, ...)
		uint width = FreeImage_GetWidth(image);
		uint height = FreeImage_GetHeight(image);
		uint bpp = FreeImage_GetBPP(image);
		auto type = FreeImage_GetImageType(image);
		if (type == FIT_BITMAP && bpp <= 24) // if less than 4x8 bits (so does not contains alpha)
		{	// make sure that alpha exists
			FIBITMAP* tmpimg = image;
			image = FreeImage_ConvertTo32Bits(image);
			FreeImage_Unload(tmpimg);
			bpp = 32;
			hasAlpha = true;
			itype = IT_BITMAP;
		}
		else if (type == FIT_UINT16 || type == FIT_INT16 || type == FIT_INT32 || type == FIT_UINT32)
		{
			// if grayscale HDR data type (e.g., HDR thermal image)
			// use float data
			FIBITMAP* tmpimg = image;
			image = FreeImage_ConvertToFloat(image);
			FreeImage_Unload(tmpimg);
			bpp = 32;
			grayscale = true;
			hasAlpha = false;
			itype = IT_FLOAT;
			// DEBUG: std::cout << "image is an HDR greyscale image." << std::endl;
		}
		uint dataSize = width * height * bpp / 8;
		uint MaskdataSize = width * height;
		BYTE *data = FreeImage_GetBits(image);

		if (lightfield->resU == 0 || lightfield->resV == 0 || lightfield->bitsPerPixel == 0) // first run!
		{
			lightfield->resU = (uint)width;
			lightfield->resV = (uint)height;
			lightfield->bitsPerPixel = (uint)bpp;
			lightfield->pageWidthPx = lightfield->resU;
			lightfield->pageHeightPx = lightfield->resV;
			lightfield->isGrayscale = grayscale;
			lightfield->hasAlpha = hasAlpha;
			lightfield->type = itype;

		}
		else if (lightfield->resU != (uint)width
			|| lightfield->resV != (uint)height
			|| lightfield->bitsPerPixel != (uint)bpp)
		{
			std::cout << "image " << imgfile << " has diferent properties (image size or bits per pixel)!" << std::endl;
			exit(-1);
		}

		// load alpha from a seperate file
		std::string alphaBase = options->GetAlphaDatabase();
		if (!alphaBase.empty())
		{
			filename.str("");
			//std::stringstream filename;
			FIBITMAP *alphaImg;
			filename << alphaBase;

			filename << imgfile;


			FREE_IMAGE_FORMAT fif = FreeImage_GetFileType(filename.str().c_str());
			alphaImg = FreeImage_Load(fif, filename.str().c_str());
			if (alphaImg)
			{

				FIBITMAP* tmpimg = alphaImg;
				alphaImg = FreeImage_ConvertToGreyscale(tmpimg);
				FreeImage_Unload(tmpimg);

				if (!options->GetFlipImage())
				{
					FreeImage_FlipVertical(alphaImg);
				}

				uint awidth = FreeImage_GetWidth(alphaImg);
				uint aheight = FreeImage_GetHeight(alphaImg);
				if (lightfield->resU != (uint)awidth || lightfield->resV != (uint)aheight )
				{
					std::cout << "alpha channel for " << imgfile << " has diferent size!" << std::endl;
				}
				else
				{
					// invert if set so in the options
					FreeImage_AdjustColors(alphaImg, 0.0, 0.0, 1.0, options->GetAlphaInvert());

					// write it in the alpha channel so that we can use it!
					FreeImage_SetChannel(image, alphaImg, FREE_IMAGE_COLOR_CHANNEL::FICC_ALPHA);

					hasAlpha = true;
					lightfield->hasAlpha = true;
				}
			}
			else
			{
				std::cout << "could not load alpha channel for image " << imgfile << "!" << std::endl;
			}
		}


		//if (lightfield->hasAlpha)
		//	FreeImage_PreMultiplyWithAlpha(image);
				

		DataCamera dataCamera;
		
		// OLD: dataCamera.data = malloc(dataSize);
		// NEW: using cuda unified memory
		if (useCUDAUnifiedMemory)
		{
			// Unified Memory: 
			// memory address can be accessed from CPU and GPU and data transfer is handeled by CUDA runtime
			// using more memory than GPU memory is possible with some limitations (with CUDA 9 it only works on compute >6 cards on Linux operating systems)
			cutilSafeCall(cudaMallocManaged(&(dataCamera.camera.data), dataSize));
			cutilSafeCall(cudaMallocManaged(&(dataCamera.camera.maskdata), MaskdataSize));
			cutilSafeCall(cudaMemset(dataCamera.camera.maskdata, 0, MaskdataSize));
			dataCamera.data = dataCamera.camera.data;
			dataCamera.Maskeddata = dataCamera.camera.maskdata;

			cudaMemAdvise(dataCamera.camera.data, dataSize, cudaMemAdviseSetReadMostly, 0);
			cudaMemAdvise(dataCamera.camera.maskdata, MaskdataSize, cudaMemAdviseSetReadMostly, 0);
		}
		else
		{
			// zero-page memory: memory on CPU-RAM that is available to cuda
			// allocation of more memory than GPU memory is possible, but slower than Unified Memory
			// memory address can be accessed from CPU and GPU
			cutilSafeCall(cudaHostAlloc(&(dataCamera.data), dataSize, cudaHostAllocMapped));
			cutilSafeCall(cudaHostGetDevicePointer(&(dataCamera.camera.data), dataCamera.data, 0));
		}
		
		

		totalDataSize += dataSize;
		

		// put image data in correct format
		uint pageLineSizeBytes = lightfield->pageWidthPx * lightfield->bitsPerPixel / 8;
		uint MaskpageLineSizeBytes = lightfield->pageWidthPx;
		uint pageLineCount = lightfield->pageHeightPx;
		uint pageSizeBytes = pageLineSizeBytes * pageLineCount;
		uint MaskpageSizeBytes = MaskpageLineSizeBytes * pageLineCount;
		uint pageResY = lightfield->resV / lightfield->pageHeightPx; // TODO check for U/V symmetry, mod
		uint pageResX = lightfield->resU / lightfield->pageWidthPx;
		for (uint yy = 0; yy < pageResY; yy++)
		{
			uint y = yy;
			if (options->GetBottomToTopGrid())
			{
				y = (pageResY - 1) - yy;
			}

			for (uint x = 0; x < pageResX; x++)
			{
				for (uint z = 0; z < pageLineCount; z++)
				{
					uint dstOffset = (x + y * pageResX) * pageSizeBytes + z * pageLineSizeBytes;
					uint srcOffset = (x + y * pageResX * pageLineCount) * pageLineSizeBytes + z * pageLineSizeBytes * pageResX;

					if (useCUDAUnifiedMemory)
						memcpy((char *)dataCamera.camera.data + dstOffset, (char *)data + srcOffset, pageLineSizeBytes); // ON GPU!
					else
						memcpy((char *)dataCamera.data + dstOffset, (char *)data + srcOffset, pageLineSizeBytes); // ON CPU
				}
			}
		}

		// unload image again (free memory ...)
		FreeImage_Unload(image);

		// asynchronous (non-blocking) upload to GPU:
		if (useCUDAUnifiedMemory && cudaDevice != -1)
		{
			cudaMemPrefetchAsync(dataCamera.camera.data, dataSize, cudaDevice, NULL); // multi-gpu is not supported, or not faster atm

			// get last cuda error and ignore!
			cudaError_t error = cudaGetLastError();
			if (error != cudaSuccess) {
				// https://devtalk.nvidia.com/default/topic/980723/cudamallocmanaged-and-cuda-8-0/
				// printf("ERROR: %s\n", cudaGetErrorString(error));
				// this seems to only work on Linux and not on Windows: https://stackoverflow.com/questions/50717306/invalid-device-ordinal-on-cudamemprefetchasync
			}
		}


		matrix m = parseMatrix(imgTreeIter->second.get_child("M3x4"));
	

		matrix invM;
		glhInvertMatrixf2(m.data, invM.data);

		//Add default corners to Mask Quadrilateral
		dataCamera.camera.ru.w = 0; dataCamera.camera.ru.x = 0; dataCamera.camera.ru.y = (float)width - 1; dataCamera.camera.ru.z = (float)width - 1;
		dataCamera.camera.rv.w = 0; dataCamera.camera.rv.x = (float)height - 1; dataCamera.camera.rv.y = (float)height - 1; dataCamera.camera.rv.z = 0;
		dataCamera.camera.meanmasked = 0.0;
		// the position data is in the last row of the inverted matrix
		dataCamera.camera.pos.x = invM.data[12];
		dataCamera.camera.pos.y = invM.data[13];
		dataCamera.camera.pos.z = invM.data[14];


			matrix intrinsic; setIdentity(intrinsic.data);
			if (0 == options->GetCameraModel().compare("rectifiedOmniCV"))
			{
				//as described in OpenCV: (when exported with omniCV)
				// https://docs.opencv.org/3.4.1/dd/d12/tutorial_omnidir_calib_main.html
				float fxFactor = options->GetFocalLengthFactorX();
				float fyFactor = options->GetFocalLengthFactorY();
				glhPerspectivef2Intrinsic(intrinsic.data, width, height, 0.1f, 1000.0f, width / fxFactor, height / fyFactor, width / 2, height / 2);
			}
			else
			{
				float fov = (float)options->GetFovRad();
				float aspectratio = (float)width / (float)height;
				glhPerspectivef2(intrinsic.data, fov, aspectratio, 0.1f, 1000.0f); 
			}
						
			
			matrix look(m); // use loaded matrix as look at matrix

			// convert from left-handed to right-handed coordinate system (e.g. data vom colmap or UnrealEngine)
			// this only converts the data camera position and the corresponding view matrices. 
			// virtual camera settings are not changed!!!
			if(options->GetConvertLHtoRHCoordinateSystem()){


				// compute forward and up vector from inverse view matrix in corresponding coordinate system
				float4 lookatVec = multiply(invM, make_float4(0, 0, 1, 0)); // dataCamera.camera.pos - make_float3(0, 0, 3);
				float4 up = multiply(invM, make_float4(0, 1, 0, 0));
				float3 lookatPos = dataCamera.camera.pos + make_float3(lookatVec);
				
				// now flip z to go from LH to RH system
				{	
					dataCamera.camera.pos.z = -dataCamera.camera.pos.z;
					lookatPos.z = -lookatPos.z;
					up.z = -up.z;
				}// 
											
				// recompute the view and inverse view matrix again 
				setIdentity(look.data);
				glhLookAtf2(look.data, dataCamera.camera.pos, lookatPos, make_float3(up) );
				glhInvertMatrixf2(look.data, invM.data);
			}

	
			//combine matrices
			glhMultMatrixf2(intrinsic.data, look.data);

			dataCamera.camera.transformation = intrinsic;

			glhInvertMatrixf2(intrinsic.data, dataCamera.camera.invertedPerspective.data);

			// also store look At vector
			float4 lookAtViewSpace = make_float4(0, 0, -1, 0);
			float4 lookAt = multiply(invM, lookAtViewSpace);
			float4 lookAtPosVS = make_float4(0, 0, -1, 1);
			float4 lookAtVS = multiply(invM, lookAtPosVS);
			float3 lookAtDir = make_float3(lookAtVS.x,lookAtVS.y,lookAtVS.z) - dataCamera.camera.pos;
			dataCamera.camera.focalPlaneDir = make_float3( lookAt.x * 100, lookAt.y * 100, lookAt.z * 100 );
			dataCamera.camera.lookAtDir = normalize( make_float3(lookAt.x, lookAt.y, lookAt.z) );

			// additionally store up vector
			float4 upViewSpace = make_float4(0, 1, 0, 0);
			float4 up = multiply(invM, upViewSpace);
			dataCamera.camera.up = normalize(make_float3(up));


		// put data Cameras into light field structure
		lightfield->dataCameras[actualIndex] = dataCamera;

		++show_progress; // update progress bar

		// increase iterator
		++count;
		++imgTreeIter;

	} // for-loop over all cameras ...
	std::cout << " done!" << std::endl;




	// TODO check geometry?!
	std::cout << "Generator: created lightfield (U: " << lightfield->resU <<
		", V: " << lightfield->resV <<
		", S: " << lightfield->resS <<
		", T: " << lightfield->resT <<
		", pageWidthPx: " << lightfield->pageWidthPx <<
		", pageHeightPx: " << lightfield->pageHeightPx <<
		")" << std::endl;

	std::cout << "Loaded " << totalDataSize << " bytes of data." << std::endl;

#ifdef _DEBUG
	{
		cudaError_t error = cudaGetLastError();
		if (error != cudaSuccess) {

			printf("ERROR: %s\n", cudaGetErrorString(error));
		}
	}
#endif

	return lightfield;
}

*/