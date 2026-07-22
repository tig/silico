/* Device HAL backend — only TU allowlisted for device headers. */
#include "hal_board.h"

#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#ifndef GCU_LED_GPIO
#define GCU_LED_GPIO 2
#endif

static void set_led(gcu_hal_t *self, int on) {
  (void)self;
  gpio_set_level(GCU_LED_GPIO, on ? 1 : 0);
}

static void delay_ms(gcu_hal_t *self, int ms) {
  (void)self;
  vTaskDelay(pdMS_TO_TICKS(ms > 0 ? ms : 1));
}

static gcu_hal_t board_hal = {
    .set_led = set_led,
    .delay_ms = delay_ms,
};

gcu_hal_t *gcu_make_board_hal(void) {
  gpio_reset_pin(GCU_LED_GPIO);
  gpio_set_direction(GCU_LED_GPIO, GPIO_MODE_OUTPUT);
  return &board_hal;
}
