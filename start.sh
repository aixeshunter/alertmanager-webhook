#!/usr/bin/env bash

if [ !${WORK_DIR} ]; then
    WORK_DIR="/opt"
fi

echo ${WORK_DIR}

python ${WORK_DIR}/alerts.py
