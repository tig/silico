/* Device HAL backend — only TU allowlisted for device headers. */
#include "hal_board.h"

#include "driver/gpio.h"
#include "esp_timer.h"
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

static int64_t now_ms(gcu_hal_t *self) {
  (void)self;
  /* esp_timer_get_time() is int64_t µs since boot; keep the division in
   * 64-bit. Do NOT narrow to long/int (32-bit here — wraps at ~24.8 days). */
  return esp_timer_get_time() / 1000;
}

static gcu_hal_t board_hal = {
    .set_led = set_led,
    .delay_ms = delay_ms,
    .now_ms = now_ms,
};

gcu_hal_t *gcu_make_board_hal(void) {
  gpio_reset_pin(GCU_LED_GPIO);
  gpio_set_direction(GCU_LED_GPIO, GPIO_MODE_OUTPUT);
  return &board_hal;
}
