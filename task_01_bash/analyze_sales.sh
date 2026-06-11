#!/bin/bash

# Setting the delimeter
IFS=$' '

# Functions to raise errors
error_incorrect_args () {
	echo Error: You need to pass correct arguments
	echo Type "-help" to see the instruction
}

error_args_number () {
	echo Error: You need to pass a file + calculation mode
	echo Type "-help" to see the instruction
}

error_file () {
	echo Error: There is no such a file
}

error_user_rights() {
	echo Error: No rights to read a file
}

error_fields_num() {
	echo Error: Incorrect number of fields
	echo The file must have exactly 5 fields
}

error_fields() {
	echo Error: Incorrect row format
}

# 1. -h parameter
if [[ "$1" == "-h" || "$1" == "-help" || "$2" == "-h" || "$2" == "-help" ]]
then
	echo Pass the path to the file as an argument
	echo Pass the second argument to make calculation:
	echo "-s" -calculate the total amount of sales
	echo "-d" -show the day with the highest sales
	echo "-p" -show the most popular product
	exit 0
fi

# 1.1 Cheking if other parameters were passed
if [ $# -ne 2 ]
then
	error_args_number
	exit 1
fi

# 2. Check file and user rights
file="$1"
arg="$2"

if [ ! -f $file ];
then
	error_file
	exit 1
fi

if [ ! -r $file ];
then
	error_user_rights
	exit 1
fi

# 3. Main calculations

total_sales=0
row_num=0

declare -A daily_day
declare -A daily_sales
declare -A products_total_sales
declare -A products_sales_amount
count=0

while IFS= read -r line;
do
	row_num=$((row_num+1))
	
	set -- $line
	fields_num=$#

	if [ $fields_num -ne 5 ]
	then
		error_fields_num
		exit 1
	fi

date=$1
day=$2
product=$3
price=$4
amount=$5

date_format='^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
day_format='^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$'
float_format='^[0-9]+(\.[0-9]+)?$'
int_format='^[0-9]+$'


if [[ ! $date =~ $date_format || ! $day =~ $day_format || ! $price =~ $float_format || ! $amount =~ $int_format ]]
then
	error_fields
	exit 1
fi

current_sale=$(bc <<< "scale=2; $price * $amount")
case $arg in
	-s)
	total_sales=$(bc <<< "scale=2; $total_sales + $current_sale")
	;;
	-d)
	daily_day[$date]=$day
	daily_sales[$date]=$(bc <<< "scale=2; ${daily_sales[$date]:-0} + $current_sale")
	;;
	-p)
	count=$(( count + 1 ))
	prev_amount=${products_sales_amount[$product]:-0}
	products_sales_amount[$product]=$(( prev_amount + amount ))

	prev_sales=${products_total_sales[$product]:-0}
	products_total_sales[$product]=$(bc <<< "scale=2; $prev_sales + $current_sale")
	;;
	*)
	error_incorrect_args
	exit 1
	;;
esac
done < "$file"

# 4. Output

case $arg in
	-s)
	echo Общая сумма продаж: $total_sales
	;;
	-d)
	max_daily_sales=0
	for k in ${!daily_sales[@]} 
	do
		v=${daily_sales[$k]}
		if (( $(bc -l <<< "$v > $max_daily_sales") ))
		then
			max_daily_sales=$v
			max_sales_date=$k
		fi
	done
	echo "День с наибольшей выручкой: $max_sales_date ${daily_day[$max_sales_date]} (сумма продаж: $max_daily_sales)"
	;;
	-p)
	max_product_amount=0
	for k in ${!products_sales_amount[@]}
	do
		v=${products_sales_amount[$k]}
		if [ $v -gt $max_product_amount ]
		then
			max_product_amount=$v
			top_product=$k
		fi
	done
	echo "Популярный товар: $top_product (количество проданных единиц: $max_product_amount, сумма продаж: ${products_total_sales[$top_product]})"
	;;
esac
