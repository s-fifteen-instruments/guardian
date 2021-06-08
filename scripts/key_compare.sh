#!/bin/bash
#
# Guardian is a quantum key distribution REST API and supporting software stack.
# Copyright (C) 2021  W. Cyrus Proctor
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

if [ "$#" -ne 2 ]; then
    echo "Illegal number of command-line inputs"
    echo "First Argument: Number of keys to request"
    echo "Second Argument: Size of keys in bits"
    exit -1
fi

# < 0 gives no output; just a return code
# == 0 gives one line output about key ID / key match
# > 0 gives more verbose output
VERBOSE=-1
# Number of keys to request
N=${1}
# Size of keys in bits
S=${2}
LOCAL_KME_ID=kme1
REMOTE_KME_ID=kme2
LOCAL_KME_HOSTNAME=${LOCAL_KME_ID}
REMOTE_KME_HOSTNAME=${REMOTE_KME_ID}
LOCAL_SAE_ID=sae1
REMOTE_SAE_ID=sae2
BASE_DIR=`pwd`
LOCAL_SAE_DIR=${base_dir}/${LOCAL_SAE_ID}
REMOTE_SAE_DIR=${base_dir}/${REMOTE_SAE_ID}

response=`curl -s "https://${LOCAL_KME_HOSTNAME}/api/v1/keys/${REMOTE_SAE_ID}/enc_keys?number=${N}&size=${S}" \
  --write-out "\n%{http_code}" \
  -H 'accept: application/json' \
  --key ${LOCAL_SAE_ID}/${LOCAL_SAE_ID}.key.pem \
  --cert ${LOCAL_SAE_ID}/${LOCAL_SAE_ID}.ca-chain.cert.pem \
  --cacert ${LOCAL_SAE_ID}/${LOCAL_SAE_ID}.ca-chain.cert.pem`

http_code=$(tail -n1 <<< "${response}")
response=$(sed '$ d' <<< "${response}")

if [ "${VERBOSE}" -gt 0 ]; then
  if [ "${http_code}" -ne "200" ]; then
    printf "Local Status Code: ${http_code}"
  fi
  printf "\nLocal KME Response to Master SAE Request:"
  printf "\n${response}"
fi

if [ "${http_code}" -ne "200" ]; then
  exit ${http_code}
fi

key_id_array=( $(echo $response | jq '.keys[]?.key_ID') )
key_array=( $(echo $response | jq '.keys[]?.key') )
key_id_array_len=${#key_id_array[@]} 

if [ "${VERBOSE}" -gt 0 ]; then
  printf "\nKey IDs:\n"
  printf "%s, " "${key_id_array[@]}"
  printf "\nKeys:\n"
  printf "%s, " "${key_array[@]}"
fi

payload_start="{\"key_IDs\": ["
payload_end="] }"

post_payload=${payload_start}
for index in "${!key_id_array[@]}"; do
  key_id_payload="{\"key_ID\": ${key_id_array[$index]}}"
  if [ "${index}" -lt "$((${key_id_array_len}-1))" ]; then
    key_id_payload="${key_id_payload},"
  fi
  post_payload="${post_payload} ${key_id_payload}"
done
post_payload="${post_payload} ${payload_end}"


if [ "${VERBOSE}" -gt 0 ]; then
  printf "\nSlave SAE POST Request Payload:\n"
  printf "${post_payload}\n"
fi

remote_response=`curl -s -X POST "https://${REMOTE_KME_HOSTNAME}/api/v1/keys/${LOCAL_SAE_ID}/dec_keys" \
  --write-out "\n%{http_code}" \
  -H 'accept: application/json' \
  -d "${post_payload}" \
  --key ${REMOTE_SAE_ID}/${REMOTE_SAE_ID}.key.pem \
  --cert ${REMOTE_SAE_ID}/${REMOTE_SAE_ID}.ca-chain.cert.pem \
  --cacert ${REMOTE_SAE_ID}/${REMOTE_SAE_ID}.ca-chain.cert.pem`

remote_http_code=$(tail -n1 <<< "${remote_response}")
remote_response=$(sed '$ d' <<< "${remote_response}")

if [ "${VERBOSE}" -gt 0 ]; then
  if [ "${remote_http_code}" -ne "200" ]; then
    printf "Remote Status Code: ${remote_http_code}"
  fi
  printf "\nRemote KME Response to Slave SAE Request:"
  printf "\n${response}"
fi

if [ "${remote_http_code}" -ne "200" ]; then
  exit ${remote_http_code}
fi

remote_key_id_array=( $(echo $remote_response | jq '.keys[]?.key_ID') )
remote_key_array=( $(echo $remote_response | jq '.keys[]?.key') )

if [ "${VERBOSE}" -gt 0 ]; then
  printf "\nRemote Key IDs:\n"
  printf "%s, " "${remote_key_id_array[@]}"
  printf "\nRemote Keys:\n"
  printf "%s, " "${remote_key_array[@]}"
  printf "\n\n"
fi

return_code=0

if [ "${key_id_array[*]}" != "${remote_key_id_array[*]}" ]; then
  if [ "${VERBOSE}" -ge 0 ]; then
    printf "Key IDs DO NOT match! "
  fi
  return_code=1
else
  if [ "${VERBOSE}" -ge 0 ]; then
    printf "Key IDs match! "
  fi
fi
  
if [ "${key_array[*]}" != "${remote_key_array[*]}" ]; then
  if [ "${VERBOSE}" -ge 0 ]; then
    printf "Keys DO NOT match!\n"
  fi
  return_code=$(($return_code+10))
else
  if [ "${VERBOSE}" -ge 0 ]; then
    printf "Keys match!\n"
  fi
fi

exit ${return_code}

