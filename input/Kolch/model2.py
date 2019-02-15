from math import *
from numpy import *
from cudasim.relations import *

def modelfunction((species1,species2,species3,species4,species5,species6,species7,species8,species9,species10,species11,species12,species13,species14,species15,species16,species17,species18,species19,species20,species21,species22,species23,species24,species25,species26,species27,species28,species29), time, parameter=(1.0,0.0038910606,8800.8254,12.874829,6017.334,5.4384396,7686.8037,8378.1143,2123.2066,0.088991477,5422.7505,25.048189,4950.1747,17.657982,5671.3432,4511.324,13119.674,7.1920631,5007.5313,6965.9208,632.51188,0.64842801,450.43603,5.1647994,12463.313,12.010199,12976.387,1.6605186,3102.3071,9681.2043,13519.007,4.0753418,8741.8547,9.3450833,9699.8676,8320.3473,872.75656,0.017410964,2013.9588,12.41417,3120.928,17.21106,9665.2665,571.28412,7.5931647,0.20545005,685.6698,2.9457857,4991.8379,2109.864,1075.3993,2.0823794,14421.281,5.8584626,2432.1789,193.30439,462.0075)):

	compartment1 = parameter[0]
	parameter1 = parameter[1]
	parameter2 = parameter[2]
	parameter3 = parameter[3]
	parameter4 = parameter[4]
	parameter5 = parameter[5]
	parameter6 = parameter[6]
	parameter7 = parameter[7]
	parameter8 = parameter[8]
	parameter9 = parameter[9]
	parameter10 = parameter[10]
	parameter11 = parameter[11]
	parameter12 = parameter[12]
	parameter13 = parameter[13]
	parameter14 = parameter[14]
	parameter15 = parameter[15]
	parameter16 = parameter[16]
	parameter17 = parameter[17]
	parameter18 = parameter[18]
	parameter19 = parameter[19]
	parameter20 = parameter[20]
	parameter21 = parameter[21]
	parameter22 = parameter[22]
	parameter23 = parameter[23]
	parameter24 = parameter[24]
	parameter25 = parameter[25]
	parameter26 = parameter[26]
	parameter27 = parameter[27]
	parameter28 = parameter[28]
	parameter29 = parameter[29]
	parameter30 = parameter[30]
	parameter31 = parameter[31]
	parameter32 = parameter[32]
	parameter33 = parameter[33]
	parameter34 = parameter[34]
	parameter35 = parameter[35]
	parameter36 = parameter[36]
	parameter37 = parameter[37]
	parameter38 = parameter[38]
	parameter39 = parameter[39]
	parameter40 = parameter[40]
	parameter41 = parameter[41]
	parameter42 = parameter[42]
	parameter43 = parameter[43]
	parameter44 = parameter[44]
	parameter45 = parameter[45]
	parameter46 = parameter[46]
	parameter47 = parameter[47]
	parameter48 = parameter[48]
	parameter49 = parameter[49]
	parameter50 = parameter[50]
	parameter51 = parameter[51]
	parameter52 = parameter[52]
	parameter53 = parameter[53]
	parameter54 = parameter[54]
	parameter55 = parameter[55]
	parameter56 = parameter[56]
	d_species1=((-1.0)*(parameter5*species1*species3)+(1.0)*(parameter6*species2)+0)/compartment1
	d_species2=((1.0)*(parameter5*species1*species3)+(-1.0)*(parameter6*species2)+0)/compartment1
	d_species3=((-1.0)*(parameter5*species1*species3)+(1.0)*(parameter6*species2)+0)/compartment1
	d_species4=((1.0)*(parameter3*species5*species2/(parameter4+species5))+(-1.0)*(parameter8*species4/(parameter7+species4))+(-1.0)*(parameter1*species4*species13/(parameter2+species4))+0)/compartment1
	d_species5=((-1.0)*(parameter3*species5*species2/(parameter4+species5))+(1.0)*(parameter8*species4/(parameter7+species4))+(-1.0)*(parameter1*species5*species13/(parameter2+species5))+0)/compartment1
	d_species6=((1.0)*(parameter9*species7*species4/(parameter10+species7))+(-1.0)*(parameter11*species6*species26/(parameter12+species6))+0)/compartment1
	d_species7=((-1.0)*(parameter9*species7*species4/(parameter10+species7))+(1.0)*(parameter11*species6*species26/(parameter12+species6))+0)/compartment1
	d_species8=((-1.0)*(parameter13*species8*species6/(parameter14+species8))+(1.0)*(parameter16*species9/(parameter15+species9))+(-1.0)*(parameter23*species8*species15/(parameter24+species8))+0)/compartment1
	d_species9=((1.0)*(parameter13*species8*species6/(parameter14+species8))+(-1.0)*(parameter16*species9/(parameter15+species9))+0)/compartment1
	d_species10=((-1.0)*(parameter17*species10*species9/(parameter18+species10))+(1.0)*(parameter20*species11/(parameter19+species11))+(-1.0)*(parameter45*species10*species23/(parameter46+species10))+0)/compartment1
	d_species11=((1.0)*(parameter17*species10*species9/(parameter18+species10))+(-1.0)*(parameter20*species11/(parameter19+species11))+(1.0)*(parameter45*species10*species23/(parameter46+species10))+0)/compartment1
	d_species12=((-1.0)*(parameter21*species12*species11/(parameter22+species12))+(1.0)*(parameter56*species13/(parameter55+species13))+0)/compartment1
	d_species13=((1.0)*(parameter21*species12*species11/(parameter22+species12))+(-1.0)*(parameter56*species13/(parameter55+species13))+0)/compartment1
	d_species14=((1.0)*(parameter1*species5*species13/(parameter2+species5))+(1.0)*(parameter1*species4*species13/(parameter2+species4))+0)/compartment1
	d_species15=((1.0)*(parameter25*species17*species29/(parameter26+species17))+(1.0)*(parameter27*species17*species28/(parameter28+species17))+(-1.0)*(parameter30*species15/(parameter29+species15))+0)/compartment1
	d_species16=((1.0)*(parameter23*species8*species15/(parameter24+species8))+0)/compartment1
	d_species17=((-1.0)*(parameter25*species17*species29/(parameter26+species17))+(-1.0)*(parameter27*species17*species28/(parameter28+species17))+(1.0)*(parameter30*species15/(parameter29+species15))+0)/compartment1
	d_species18=((1.0)*(parameter31*species19*species27/(parameter32+species19))+(1.0)*(parameter33*species19*species28/(parameter34+species19))+(-1.0)*(parameter36*species18/(parameter35+species18))+0)/compartment1
	d_species19=((-1.0)*(parameter31*species19*species27/(parameter32+species19))+(-1.0)*(parameter33*species19*species28/(parameter34+species19))+(1.0)*(parameter36*species18/(parameter35+species18))+0)/compartment1
	d_species20=((1.0)*(parameter37*species21*species18/(parameter38+species21))+(-1.0)*(parameter39*species20*species26/(parameter40+species20))+(1.0)*(parameter51*species21*species24/(parameter52+species21))+0)/compartment1
	d_species21=((-1.0)*(parameter37*species21*species18/(parameter38+species21))+(1.0)*(parameter39*species20*species26/(parameter40+species20))+(-1.0)*(parameter51*species21*species24/(parameter52+species21))+0)/compartment1
	d_species22=((-1.0)*(parameter41*species22*species20/(parameter42+species22))+(1.0)*(parameter44*species23/(parameter43+species23))+(-1.0)*(parameter53*species22*species6/(parameter54+species22))+0)/compartment1
	d_species23=((1.0)*(parameter41*species22*species20/(parameter42+species22))+(-1.0)*(parameter44*species23/(parameter43+species23))+(1.0)*(parameter53*species22*species6/(parameter54+species22))+0)/compartment1
	d_species24=((1.0)*(parameter47*species25*species2/(parameter48+species25))+(-1.0)*(parameter49*species24/(parameter50+species24))+0)/compartment1
	d_species25=((-1.0)*(parameter47*species25*species2/(parameter48+species25))+(1.0)*(parameter49*species24/(parameter50+species24))+0)/compartment1
	d_species26=(0)/compartment1
	d_species27=(0)/compartment1
	d_species28=(0)/compartment1
	d_species29=(0)/compartment1

	return(d_species1,d_species2,d_species3,d_species4,d_species5,d_species6,d_species7,d_species8,d_species9,d_species10,d_species11,d_species12,d_species13,d_species14,d_species15,d_species16,d_species17,d_species18,d_species19,d_species20,d_species21,d_species22,d_species23,d_species24,d_species25,d_species26,d_species27,d_species28,d_species29)

def rules((species1,species2,species3,species4,species5,species6,species7,species8,species9,species10,species11,species12,species13,species14,species15,species16,species17,species18,species19,species20,species21,species22,species23,species24,species25,species26,species27,species28,species29), (compartment1,parameter1,parameter2,parameter3,parameter4,parameter5,parameter6,parameter7,parameter8,parameter9,parameter10,parameter11,parameter12,parameter13,parameter14,parameter15,parameter16,parameter17,parameter18,parameter19,parameter20,parameter21,parameter22,parameter23,parameter24,parameter25,parameter26,parameter27,parameter28,parameter29,parameter30,parameter31,parameter32,parameter33,parameter34,parameter35,parameter36,parameter37,parameter38,parameter39,parameter40,parameter41,parameter42,parameter43,parameter44,parameter45,parameter46,parameter47,parameter48,parameter49,parameter50,parameter51,parameter52,parameter53,parameter54,parameter55,parameter56), time):



	return((species1,species2,species3,species4,species5,species6,species7,species8,species9,species10,species11,species12,species13,species14,species15,species16,species17,species18,species19,species20,species21,species22,species23,species24,species25,species26,species27,species28,species29),(compartment1,parameter1,parameter2,parameter3,parameter4,parameter5,parameter6,parameter7,parameter8,parameter9,parameter10,parameter11,parameter12,parameter13,parameter14,parameter15,parameter16,parameter17,parameter18,parameter19,parameter20,parameter21,parameter22,parameter23,parameter24,parameter25,parameter26,parameter27,parameter28,parameter29,parameter30,parameter31,parameter32,parameter33,parameter34,parameter35,parameter36,parameter37,parameter38,parameter39,parameter40,parameter41,parameter42,parameter43,parameter44,parameter45,parameter46,parameter47,parameter48,parameter49,parameter50,parameter51,parameter52,parameter53,parameter54,parameter55,parameter56))

