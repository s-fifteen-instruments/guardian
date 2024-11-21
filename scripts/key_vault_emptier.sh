#!/bin/bash

# This is a script to check the number of keys in the guardian key store and
# if the number is >95% of the max number of keys, empty out 1% of the keys
#
# To periodically run script, add to crontab or install as a service.
#
# Changelog:
#       2024-10-18 Syed: Initial script for guardian key vault emptier 

hostnameA=e.qkd.external
hostnameB=c.qkd.external
max_limit_percent=95
empty_out_percent=1
sae_idB=SAE-S15-Test-003-sae3
sae_idA=SAE-S15-Test-005-sae5
certs_dir=~/certs
A_key=$certs_dir/$sae_idA.key.pem
A_cert=$certs_dir/$sae_idA.cert.pem
B_key=$certs_dir/$sae_idB.key.pem
B_cert=$certs_dir/$sae_idB.cert.pem
CERT=$certs_dir/full-chain.cert.pem
CERT_FLAGSA="--cacert ${CERT}"
CERT_FLAGSB="--cacert ${CERT}"
A_KEY_FLAGS="--cert ${A_cert} --key ${A_key}"
B_KEY_FLAGS="--cert ${B_cert} --key ${B_key}"
progA="curl -s ${CERT_FLAGSA} ${A_KEY_FLAGS}"
progB="curl -s ${CERT_FLAGSB} ${B_KEY_FLAGS}"



protocol=https://
end_point_head=api/v1/keys/
addA_base=${protocol}${hostnameA}/${end_point_head}${sae_idB}/
addB_base=${protocol}${hostnameB}/${end_point_head}${sae_idA}/
stat=status
enc=enc_keys
dec=dec_keys
#echo $progA ${addA_base}${stat}
#echo $progB ${addB_base}${stat}
qkd_statusA=$($progA ${addA_base}${stat})
qkd_statusB=$($progB ${addB_base}${stat})

#echo $qkd_statusA
#echo $qkd_statusB
ISE='Internal Server Error'
max_key_size=65536
date=$(date -R)

if [[ $qkd_statusA == $ISE ]] ; then
    AB_resp=$(${progA} ${addA_base}${enc}"?number=2&size="$max_key_size)
    echo "$date $AB_resp"
    for i in $(echo $AB_resp | jq -r ".keys[].key_ID"); do
        AB_reply=$(${progB} ${addB_base}${dec}"?key_ID="$i)
        echo "$date $AB_reply"
        sleep 1
    done
fi

if [[ $qkd_statusB == $ISE ]] ; then 
    BA_resp=$(${progB} ${addB_base}${enc}"?number=2&size="$max_key_size)
    echo "$date $BA_resp"
    for i in $(echo $BA_resp | jq -r ".keys[].key_ID"); do
        BA_reply=$(${progA} ${addA_base}${dec}"?key_ID="$i)
        echo "$date $BA_reply"
        sleep 1
    done
fi

if [[ $qkd_statusB == $ISE || $qkd_statusA == $ISE ]] ; then 
    echo "$date ISE"
    exit 0
fi

key_countA=$(echo $qkd_statusA | jq -r .stored_key_count?)
key_countB=$(echo $qkd_statusB | jq -r .stored_key_count?)
max_key_countA=$(echo $qkd_statusA | jq -r .max_key_count?)
max_key_countB=$(echo $qkd_statusB | jq -r .max_key_count?)
key_sizeA=$(echo $qkd_statusA | jq -r .key_size?)
key_sizeB=$(echo $qkd_statusB | jq -r .key_size?)
max_key_sizeA=$(echo $qkd_statusA | jq -r .max_key_size?)
max_key_sizeB=$(echo $qkd_statusB | jq -r .max_key_size?)
max_key_per_req_A=$(echo $qkd_statusA | jq -r .max_key_per_request?)
max_key_per_req_B=$(echo $qkd_statusB | jq -r .max_key_per_request?)

key_compA=$(( $max_key_countA * $max_limit_percent / 100 ))
key_compB=$(( $max_key_countB * $max_limit_percent / 100 ))
bits_to_emptyA=$(( $max_key_countA * $empty_out_percent / 100 * $key_sizeA ))
bits_to_emptyB=$(( $max_key_countB * $empty_out_percent / 100 * $key_sizeB ))
num_keys_to_emptyA=$(( $bits_to_emptyA / $max_key_sizeA ))
num_keys_to_emptyB=$(( $bits_to_emptyB / $max_key_sizeB ))
AB_resp=
BA_resp=


#exit 0
if [[ ${key_countA} -gt ${key_compA} ]]; then
	if [[ $num_keys_to_emptyA -gt 0 && $num_keys_to_emptyA -lt $max_key_per_req_A ]] ; then
		AB_resp=$(${progA} ${addA_base}${enc}"?number="$num_keys_to_emptyA"&size="$max_key_sizeA)
		echo "$date $AB_resp"
	fi
fi

if [[ ${key_countB} -gt ${key_compB} ]]; then
	if [[ $num_keys_to_emptyB -gt 0 && $num_keys_to_emptyB -lt $max_key_per_req_B ]] ; then
		BA_resp=$(${progB} ${addB_base}${enc}"?number="$num_keys_to_emptyB"&size="$max_key_sizeB)
		echo "$date $BA_resp"
	fi
fi

if [[ ! -z ${AB_resp} ]] ; then
	for i in $(echo $AB_resp | jq -r ".keys[].key_ID"); do
		AB_reply=$(${progB} ${addB_base}${dec}"?key_ID="$i)
		echo "$date $AB_reply"
		sleep 1
	done
fi

if [[ ! -z ${BA_resp} ]] ; then
	for i in $(echo $BA_resp | jq -r ".keys[].key_ID"); do
		BA_reply=$(${progA} ${addA_base}${dec}"?key_ID="$i)
		echo "$date $BA_reply"
		sleep 1
	done
fi
