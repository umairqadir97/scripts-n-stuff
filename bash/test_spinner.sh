#! /bin/bash

# Set Variables/Arrays
SPIN_ARR=(○ ◎ ◉ ● ◉ ◎)
SPIN_CYCLE="0"

# Run something to test against
#test_process() {
#sleep 20 &
#}

# Set up spinner
test_spinner() {
while [ "${SPIN_CYCLE}" -le "3" ]
do
  for ELEMENT in "${SPIN_ARR[@]}"
  do
    if [ "${ELEMENT}" == "${SPIN_ARR[0]}" ]; then
      SPIN_CYCLE="$((${SPIN_CYCLE} + 1))"
    fi
    echo -ne "\rRunning: ${ELEMENT} "
    sleep 1
  done
done
}

test_spinner
