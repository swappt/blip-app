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

openssl aes-256-ecb -d -in org-swappt-blip-app.keystore.aes-256-ecb -out org-swappt-blip-app.keystore

export P4A_RELEASE_KEYSTORE=~/blip-app/org-swappt-blip-app.keystore
export P4A_RELEASE_KEYALIAS=blip
export P4A_RELEASE_KEYSTORE_PASSWD=$2
export P4A_RELEASE_KEYALIAS_PASSWD=$2

buildozer android $1

rm org-swappt-blip-app.keystore
