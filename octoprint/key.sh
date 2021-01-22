
KEY=$(cat /octoprint/octoprint/config.yaml | grep key| cut -d ":" -f2 | xargs)

while ["$KEY" != '']
do
	sleep 5
	KEY=$(cat /octoprint/octoprint/config.yaml | grep key| cut -d ":" -f2 | xargs)
done

echo "Setting key to $KEY in file $ENV_FILE"
echo "OCTOPRINT_KEY=$KEY">$ENV_FILE
