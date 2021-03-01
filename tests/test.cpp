//#include "wingdi.h"
#include "gtest/gtest.h"
#include "LFGenerator.h"


#define EXPECT_NEAR_VEC( v0, v1 ) \
	EXPECT_NEAR(v0.x, v1.x, FLT_EPSILON * 100); \
	EXPECT_NEAR(v0.y, v1.y, FLT_EPSILON * 100); \
	EXPECT_NEAR(v0.z, v1.z, FLT_EPSILON * 100);

TEST(LFGeneratorTest, LoadMatrices) {


	LFGenerator generator;
	auto lf = generator.Generate("../data/Hellmonsoedt_pose_corr.json", "../data/Hellmonsoedt_ldr_r512/" );

	EXPECT_EQ(lf->GetSize(), 382);

	// position 0: 0.710525669412324	0.604463882989740	-58.0499999429207
	auto pos0 = lf->GetPosition(0);
	EXPECT_NEAR(pos0.x, 0.710525669412324, FLT_EPSILON*100);
	EXPECT_NEAR(pos0.y, 0.604463882989740, FLT_EPSILON*100);
	EXPECT_NEAR(pos0.z, -58.0499999429207, FLT_EPSILON*100);
	// forward 0: 0.162379453346099	0.191677628044390	0.967932210175724
	auto forward0 = lf->GetForward(0);
	EXPECT_NEAR_VEC(forward0, glm::vec3(0.162379453346099,	0.191677628044390,	0.967932210175724) );
	// up: 0.812924527982227	0.530011609674120	-0.241332633933686
	auto up0 = lf->GetUp(0);
	EXPECT_NEAR_VEC(up0, glm::vec3(0.812924527982227,	0.530011609674120, - 0.241332633933686));


	// position 1: 0.753704012523495	0.738250940313606	-49.9500037693784
	auto pos1 = lf->GetPosition(1);
	EXPECT_NEAR(pos1.x, 0.753704012523495, FLT_EPSILON*100);
	EXPECT_NEAR(pos1.y, 0.738250940313606, FLT_EPSILON*100);
	EXPECT_NEAR(pos1.z, -49.9500037693784, FLT_EPSILON*100);
	// forward 1: 0.166029251710846	0.188525036925972	0.967932145733675
	auto forward1 = lf->GetForward(1);
	EXPECT_NEAR_VEC(forward1, glm::vec3(0.166029251710846,	0.188525036925972,	0.967932145733675));
	// up: 0.822949622182668	0.514307799812439	-0.241332630369507
	auto up1 = lf->GetUp(1);
	EXPECT_NEAR_VEC(up1, glm::vec3(0.822949622182668,	0.514307799812439, - 0.241332630369507));


	EXPECT_EQ(1, 1);
	EXPECT_TRUE(true);

	delete lf;
}

int main(int argc, char **argv) {
	::testing::InitGoogleTest(&argc, argv);
	return RUN_ALL_TESTS();
}