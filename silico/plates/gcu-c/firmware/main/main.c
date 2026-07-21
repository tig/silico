#include "gcu/defaults.h"
#include "gcu/hal.h"
#include "gcu/version.h"
#include "hal_board.h"

#include <stdio.h>

/* domain symbols from src/domain.c */
typedef struct {
  gcu_hal_t *hal;
  int tick_count;
  int led_on;
  int tick_sleep_ms;
} gcu_state_t;

void gcu_identity_line(char *out, int out_len);
void gcu_init(gcu_state_t *st, gcu_hal_t *hal);
void gcu_tick(gcu_state_t *st);
int gcu_tick_sleep_ms(const gcu_state_t *st);

void app_main(void) {
  char id[64];
  gcu_state_t st;
  gcu_hal_t *hal = gcu_make_board_hal();

  gcu_identity_line(id, (int)sizeof id);
  printf("%s\n", id);
  fflush(stdout);

  gcu_init(&st, hal);
  for (;;) {
    gcu_tick(&st);
    if (hal && hal->delay_ms) {
      hal->delay_ms(hal, gcu_tick_sleep_ms(&st));
    }
  }
}
