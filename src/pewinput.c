
#include "pewinput.h"


int open_uinput(void) {
    int uinput_fd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
    return uinput_fd;
}

int enable_event(int uinput_fd, uint16_t event_type, uint16_t event_code) {
    unsigned long input_type;
    switch (event_type) {
        case EV_KEY:
            ioctl(uinput_fd, UI_SET_EVBIT, EV_REP);
            input_type = UI_SET_KEYBIT;
            break;
        case EV_REL:
            input_type = UI_SET_RELBIT;
            break;
        case EV_ABS:
            input_type = UI_SET_ABSBIT;
            break;
        case EV_MSC:
            input_type = UI_SET_MSCBIT;
            break;
        case EV_SW:
            input_type = UI_SET_SWBIT;
            break;
        case EV_LED:
            input_type = UI_SET_LEDBIT;
            break;
        case EV_SND:
            input_type = UI_SET_SNDBIT;
            break;
        case EV_FF:
            input_type = UI_SET_FFBIT;
            break;
    }
    ioctl(uinput_fd, UI_SET_EVBIT, event_type);
    return ioctl(uinput_fd, input_type, event_code);
}

int create_device(int uinput_fd, const char* name) {
    struct uinput_setup usetup;
    memset(&usetup, 0, sizeof(usetup));
    usetup.id.bustype = BUS_USB;
    usetup.id.vendor = 0x0;
    usetup.id.product = 0x0;
    strcpy(usetup.name, name);

    ioctl(uinput_fd, UI_DEV_SETUP, &usetup);
    int err = ioctl(uinput_fd, UI_DEV_CREATE);
    sleep(1);
    return err;
}

void send_event(int uinput_fd, uint16_t event_type, uint16_t event_code, int32_t event_value) {
    struct input_event event;
    event.type = event_type;
    event.code = event_code;
    event.value = event_value;
    event.time.tv_sec = 0;
    event.time.tv_usec = 0;

    write(uinput_fd, &event, sizeof(event));
}

void flush(int uinput_fd) {
    send_event(uinput_fd, EV_SYN, SYN_REPORT, 0);
}

int destroy_device(int uinput_fd) {
    return ioctl(uinput_fd, UI_DEV_DESTROY);
}

int close_uinput(int uinput_fd) {
    return close(uinput_fd);
}
