# this script is for building the app for android through Linux #
#$ debug $1
#$ passwd $2
echo 'Copying androidmanifest template...'
cp AndroidManifest.tmpl.xml .buildozer/android/platform/build/dists/blipapp/templates
echo 'Finished copying the manifest template.'
echo 'Deleting compiler-end data, if present...'
rm .data.json
rm chk.json
echo 'Deleted data.'
echo 'Build process beginning...'

openssl aes-256-ecb -d -in blip-p.keystore.aes-256-ecb -out blip-p.keystore

export P4A_RELEASE_KEYSTORE=~/blip-app/blip-p.keystore
export P4A_RELEASE_KEYALIAS=blip-p
export P4A_RELEASE_KEYSTORE_PASSWD=$2
export P4A_RELEASE_KEYALIAS_PASSWD=$2

buildozer android $1

rm blip-p.keystore
