# Lab D50 -> XYZ @ D50
# from http://www.brucelindbloom.com/index.html?Eqn_ChromAdapt.html
def LabD50toXYZD50(CIEL,CIEa,CIEb):
	eps = 0.008856
	kappa = 903.3
	fy = (CIEL + 16.0) / 116.0
	fx = CIEa / 500.0 + fy
	fz = fy - CIEb / 200.0

	if (pow(fx,3) > eps):
		xr = pow(fx,3)
	else:
		xr = (116.0 * fx -16.0) / kappa

	if (CIEL > kappa * eps):
		yr = pow((CIEL + 16.0) / 116.0,3)
	else:
		yr = CIEL / kappa

	if (pow(fz,3) > eps):
		zr = pow(fz,3)
	else:
		zr = (116.0 * fz - 16.0) / kappa


	X = 96.422 * xr
	Y = 100 * yr
	Z = 82.521 * zr

	return[X,Y,Z]


# XYZ @ D50 -> XYZ @ D65
# Chromatic adaptation
# formula from http://www.brucelindbloom.com/index.html?Eqn_ChromAdapt.html
# bradford coefficients:
#      0.9555766 -0.0230393  0.0631636
# M = -0.0282895  1.0099416  0.0210077
#      0.0122982 -0.0204830  1.3299098
def XYZD50toXYZD65(Xs,Ys,Zs):
	Xd = 0.9555766 * Xs -0.0230393 * Ys + 0.0631636 * Zs
	Yd = -0.0282895 * Xs + 1.0099416 * Ys + 0.0210077 * Zs
	Zd = 0.0122982 * Xs -0.0204830 * Ys + 1.3299098 * Zs

	return [Xd,Yd,Zd]

# XYZ @ D65 - Lab D65
# reference white point @D65: X=95.047, Y=100, Z=108.883
# from http://www.brucelindbloom.com/index.html?Eqn_ChromAdapt.html
def XYZD65toLabD65(X,Y,Z):
	eps = 0.008856
	kappa = 903.3
	xr = X / 95.047
	yr = Y / 100
	zr = Z / 108.883

	if (xr > eps):
		fx = pow(xr,1/3.0)
	else:
		fx = (kappa * xr + 16.0) / 116.0

	if (yr > eps):
		fy = pow(yr,1/3.0)
	else:
		fy = (kappa * yr + 16.0) / 116.0

	if (zr > eps):
		fz = pow(zr,1/3.0)
	else:
		fz = (kappa * zr + 16.0) / 116.0

	CIEL = 116.0 * fy - 16.0
	CIEa = 500 * (fx - fy)
	CIEb = 200 * (fy - fz)

	return [CIEL,CIEa,CIEb]
