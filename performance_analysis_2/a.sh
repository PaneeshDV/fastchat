grep -E 2022 "$1" > a.txt
sed -E s/"2022-11-.. ..:..:"//g -i a.txt
sed s/,//g -i a.txt
grep -E "h[0-9]+" a.txt > b.txt
echo "EXIT" >> b.txt
python3 analy.py < b.txt > k.txt