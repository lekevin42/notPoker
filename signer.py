import os, random, struct
import sys
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA 
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA512
from base64 import b64encode, b64decode 

##################################################
# Loads the RSA key object from the location
# @param keyPath - the path of the key
# @return - the RSA key object with the loaded key
##################################################
def loadKey(keyPath):
	
	# The RSA key
	key = None
	
	# Open the key file
	with open(keyPath, 'r') as keyFile:
		
		# Read the key file
		keyFileContent = keyFile.read()
		
		# Decode the key
		decodedKey = b64decode(keyFileContent)
		
		# Load the key
		key = RSA.importKey(decodedKey)

	# Return the key
	return key	
		

##################################################
# Signs the string using an RSA private key
# @param sigKey - the signature key
# @param string - the string
##################################################
def digSig(sigKey, string):
	return sigKey.sign(string, '')
	

##########################################################
# Returns the file signature
# @param fileName - the name of the file
# @param privKey - the private key to sign the file with
# @return fileSig - the file signature
##########################################################
def getFileSig(fileName, privKey):
	with open(fileName, "r") as file:
		contents = file.read()
		
	hash = SHA512.new(contents).hexdigest()
	
	return digSig(privKey, hash)
	
###########################################################
# Verifies the signature of the file
# @param fileName - the name of the file
# @param pubKey - the public key to use for verification
# @param signature - the signature of the file to verify
##########################################################
def verifyFileSig(fileName, pubKey, signature):
	with open(fileName, "r") as file:
		contents = file.read()
		
	hash = SHA512.new(contents).hexdigest()
	
	print(hash, signature, pubKey)
	
	return verifySig(hash, signature, pubKey)
	
	
############################################
# Saves the digital signature to a file
# @param fileName - the name of the file
# @param signature - the signature to save
############################################
def saveSig(fileName, signature):
	with open(fileName, "w") as file:
		file.write(str(signature[0]))
	

###########################################
# Loads the signature and converts it into
# a tuple
# @param fileName - the file containing the
# signature
# @return - the signature
###########################################
def loadSig(fileName):
	with open(fileName, "r") as file:
		contents = file.read()
		
	return (int(contents),)	
	
	
#################################################
# Verifies the signature
# @param theHash - the hash 
# @param sig - the signature to check against
# @param veriKey - the verification key
# @return - True if the signature matched and
# false otherwise
#################################################
def verifySig(theHash, sig, veriKey):
	return veriKey.verify(theHash, sig)		


# The main function
def main():
	
	# Make sure that all the arguments have been provided
	if len(sys.argv) < 5:
		print "USAGE: " + sys.argv[0] + " <KEY FILE NAME> <SIGNATURE FILE NAME> <INPUT FILE NAME>"
		exit(-1)
	
	# The key file
	keyFileName = sys.argv[1]
	
	# Signature file name
	sigFileName = sys.argv[2]
	
	# The input file name
	inputFileName = sys.argv[3]
	
	# The mode i.e., sign or verify
	mode = sys.argv[4]

	key = loadKey(keyFileName)
	# We are signing
	if mode == "sign":
		sig = getFileSig(inputFileName, key)
		saveSig(sigFileName, sig)
		
		print "Signature saved to file ", sigFileName

	# We are verifying the signature
	elif mode == "verify":
		oldSig = loadSig(sigFileName)
		if verifyFileSig(inputFileName, key, oldSig):
			print "Matches!"
			
		else:
			print "Does not match!"
		
	else:
		print "Invalid mode ", mode	

### Call the main function ####
if __name__ == "__main__":
	main()
