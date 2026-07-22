#include "gcu/defaults.h"
#include "gcu/domain.h"
#include "gcu/hal.h"
#include "gcu/version.h"
#include "hal_board.h"

#include <stdio.h>

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
