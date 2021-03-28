
today=$(date +"%Y/%m/%d")
yesterday=$(date -d "1 day ago" +"%Y/%m/%d")

echo "Launching from $yesterday until $today"
python3 main.py \
	-t \
	-a \
	-g \
	-a \
	-c \
	-s "$yesterday-00:00:00" \
	-e "$today-00:00:00"
