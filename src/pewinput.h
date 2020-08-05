
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

#include <linux/uinput.h>


extern int open_uinput(void);
extern int enable_event(int uinput_fd, uint16_t event_type, uint16_t event_code);
extern int create_device(int uinput_fd, const char* name);
extern void send_event(int uinput_fd, uint16_t event_type, uint16_t event_code, int32_t event_value);
extern void flush(int uinput_fd);
extern int destroy_device(int uinput_fd);
extern int close_uinput(int uinput_fd);
