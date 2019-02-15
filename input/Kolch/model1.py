from math import *
from numpy import *
from cudasim.relations import *

def modelfunction((species1,species2,species3,species4,species5,species6,species7,species8,species9,species10,species11,species12,species13,species14,species15,species16,species17,species18,species19,species20,species21,species22,species23,species24,species25,species26,species27), time, parameter=(1.0,0.0010572843,18279.761,0.73061493,738.12761,1.6665105,687.15641,168.87001,259.0733,0.0504318,4711.3334,17.312119,7248.9633,6.3224454,4666.8334,8103.3883,4100.5039,7.7221471,9817.135,9470.8799,613.43383,0.81973062,602.79637,10.240582,9559.3224,6.4116281,2818.0672,13.361394,6087.5111,5165.9729,28608.154,0.06774163,10088.056,0.036278847,2626.6583,12426.919,20.571563,0.0025122156,4403.7089,16.594473,2929.1431,13.275618,1356.9518,867.64411,7.2599818,0.31665621,366.30473,8.2056076,2999.4779,466.82131,73.773914)):

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
	d_species1=((-1.0)*(parameter5*species1*species3)+(1.0)*(parameter6*species2)+0)/compartment1
	d_species2=((1.0)*(parameter5*species1*species3)+(-1.0)*(parameter6*species2)+0)/compartment1
	d_species3=((-1.0)*(parameter5*species1*species3)+(1.0)*(parameter6*species2)+0)/compartment1
	d_species4=((1.0)*(parameter3*species2*species5/(parameter4+species5))+(-1.0)*(parameter8*species4/(parameter7+species4))+(-1.0)*(parameter1*species4*species13/(parameter2+species4))+0)/compartment1
	d_species5=((-1.0)*(parameter3*species2*species5/(parameter4+species5))+(1.0)*(parameter8*species4/(parameter7+species4))+(-1.0)*(parameter1*species13*species5/(parameter2+species5))+0)/compartment1
	d_species6=((1.0)*(parameter9*species4*species7/(parameter10+species7))+(-1.0)*(parameter11*species24*species6/(parameter12+species6))+0)/compartment1
	d_species7=((-1.0)*(parameter9*species4*species7/(parameter10+species7))+(1.0)*(parameter11*species24*species6/(parameter12+species6))+0)/compartment1
	d_species8=((-1.0)*(parameter13*species8*species6/(parameter14+species8))+(1.0)*(parameter16*species9/(parameter15+species9))+(-1.0)*(parameter23*species8*species15/(parameter24+species8))+0)/compartment1
	d_species9=((1.0)*(parameter13*species8*species6/(parameter14+species8))+(-1.0)*(parameter16*species9/(parameter15+species9))+0)/compartment1
	d_species10=((-1.0)*(parameter17*species9*species10/(parameter18+species10))+(1.0)*(parameter20*species11/(parameter19+species11))+(-1.0)*(parameter45*species10*species23/(parameter46+species10))+0)/compartment1
	d_species11=((1.0)*(parameter17*species9*species10/(parameter18+species10))+(-1.0)*(parameter20*species11/(parameter19+species11))+(1.0)*(parameter45*species10*species23/(parameter46+species10))+0)/compartment1
	d_species12=((-1.0)*(parameter21*species12*species11/(parameter22+species12))+(1.0)*(parameter49*species13/(parameter50+species13))+0)/compartment1
	d_species13=((1.0)*(parameter21*species12*species11/(parameter22+species12))+(-1.0)*(parameter49*species13/(parameter50+species13))+0)/compartment1
	d_species14=((1.0)*(parameter1*species13*species5/(parameter2+species5))+(1.0)*(parameter1*species4*species13/(parameter2+species4))+0)/compartment1
	d_species15=((1.0)*(parameter25*species17*species27/(parameter26+species17))+(1.0)*(parameter27*species17*species26/(parameter28+species17))+(-1.0)*(parameter30*species15/(parameter29+species15))+0)/compartment1
	d_species16=((1.0)*(parameter23*species8*species15/(parameter24+species8))+0)/compartment1
	d_species17=((-1.0)*(parameter25*species17*species27/(parameter26+species17))+(-1.0)*(parameter27*species17*species26/(parameter28+species17))+(1.0)*(parameter30*species15/(parameter29+species15))+0)/compartment1
	d_species18=((1.0)*(parameter31*species19*species25/(parameter32+species19))+(1.0)*(parameter33*species19*species26/(parameter34+species19))+(-1.0)*(parameter36*species18/(parameter35+species18))+0)/compartment1
	d_species19=((-1.0)*(parameter31*species19*species25/(parameter32+species19))+(-1.0)*(parameter33*species19*species26/(parameter34+species19))+(1.0)*(parameter36*species18/(parameter35+species18))+0)/compartment1
	d_species20=((1.0)*(parameter37*species21*species18/(parameter38+species21))+(-1.0)*(parameter39*species20*species24/(parameter40+species20))+0)/compartment1
	d_species21=((-1.0)*(parameter37*species21*species18/(parameter38+species21))+(1.0)*(parameter39*species20*species24/(parameter40+species20))+0)/compartment1
	d_species22=((-1.0)*(parameter41*species22*species20/(parameter42+species22))+(1.0)*(parameter44*species23/(parameter43+species23))+(-1.0)*(parameter47*species22*species6/(parameter48+species22))+0)/compartment1
	d_species23=((1.0)*(parameter41*species22*species20/(parameter42+species22))+(-1.0)*(parameter44*species23/(parameter43+species23))+(1.0)*(parameter47*species22*species6/(parameter48+species22))+0)/compartment1
	d_species24=(0)/compartment1
	d_species25=(0)/compartment1
	d_species26=(0)/compartment1
	d_species27=(0)/compartment1

	return(d_species1,d_species2,d_species3,d_species4,d_species5,d_species6,d_species7,d_species8,d_species9,d_species10,d_species11,d_species12,d_species13,d_species14,d_species15,d_species16,d_species17,d_species18,d_species19,d_species20,d_species21,d_species22,d_species23,d_species24,d_species25,d_species26,d_species27)

def rules((species1,species2,species3,species4,species5,species6,species7,species8,species9,species10,species11,species12,species13,species14,species15,species16,species17,species18,species19,species20,species21,species22,species23,species24,species25,species26,species27), (compartment1,parameter1,parameter2,parameter3,parameter4,parameter5,parameter6,parameter7,parameter8,parameter9,parameter10,parameter11,parameter12,parameter13,parameter14,parameter15,parameter16,parameter17,parameter18,parameter19,parameter20,parameter21,parameter22,parameter23,parameter24,parameter25,parameter26,parameter27,parameter28,parameter29,parameter30,parameter31,parameter32,parameter33,parameter34,parameter35,parameter36,parameter37,parameter38,parameter39,parameter40,parameter41,parameter42,parameter43,parameter44,parameter45,parameter46,parameter47,parameter48,parameter49,parameter50), time):



	return((species1,species2,species3,species4,species5,species6,species7,species8,species9,species10,species11,species12,species13,species14,species15,species16,species17,species18,species19,species20,species21,species22,species23,species24,species25,species26,species27),(compartment1,parameter1,parameter2,parameter3,parameter4,parameter5,parameter6,parameter7,parameter8,parameter9,parameter10,parameter11,parameter12,parameter13,parameter14,parameter15,parameter16,parameter17,parameter18,parameter19,parameter20,parameter21,parameter22,parameter23,parameter24,parameter25,parameter26,parameter27,parameter28,parameter29,parameter30,parameter31,parameter32,parameter33,parameter34,parameter35,parameter36,parameter37,parameter38,parameter39,parameter40,parameter41,parameter42,parameter43,parameter44,parameter45,parameter46,parameter47,parameter48,parameter49,parameter50))

