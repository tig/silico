# ESP-IDF project root. Configure with idf.py from an ESP-IDF environment.
# Minimal hello-metal: identity on UART, optional LED via hal_board.

cmake_minimum_required(VERSION 3.16)

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(gcu_c)
