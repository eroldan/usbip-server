#!/usr/bin/env bash

# CPU core to use for handling audio IRQs
AUDIO_CORE=2      # (cpu0=0, cpu1=1, cpu2=2, ...)
ETHERNET_CORE=3   # keep NIC separate from audio

# Realtime priority value
RT_PRIO=90        # must be lower than JACK or pipewire threads if used

# === function to pin and chrt an IRQ ===
tune_irq() {
  local irq=$1
  local core=$2

  echo "Tuning IRQ $irq to CPU core $core"

  # pin the IRQ
  mask=$((1<<core))
  echo $mask
  #echo $(printf "%x" $mask) > /proc/irq/$irq/smp_affinity_list
  echo $core > /proc/irq/$irq/smp_affinity_list


  # assign realtime priority
  chrt -f -p $RT_PRIO `pgrep -f "irq/$irq"` 2>/dev/null
}

echo "-------- USB Audio IRQs --------"
# find USB IRQs that have audio class devices
for usb_irq in $(awk '/_hcd/ {print $1}' ORS=' ' /proc/interrupts | tr -d ':'); do
    # crude: we assume all USB IRQs matter (lsusb -t could be filtered here)
    tune_irq $usb_irq $AUDIO_CORE
done

echo "-------- Ethernet IRQs --------"
# pick NIC interrupts (adapt regex if needed)
for nic_irq in $(awk '/eth|enp/ {print $1}' ORS=' ' /proc/interrupts | tr -d ':'); do
    tune_irq $nic_irq $ETHERNET_CORE
done

echo "Done."
