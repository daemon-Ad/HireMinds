import { Directive, ElementRef, forwardRef, OnDestroy, AfterViewInit } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import * as flatpickrModule from 'flatpickr';
import { Instance } from 'flatpickr/dist/types/instance';

const flatpickr = (flatpickrModule as any).default || flatpickrModule;

@Directive({
  selector: '[appDatetimePicker]',
  standalone: true,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => DatetimePickerDirective),
      multi: true
    }
  ]
})
export class DatetimePickerDirective implements AfterViewInit, OnDestroy, ControlValueAccessor {
  private fpInstance: Instance | null = null;
  private pendingValue: string = '';
  private onChange: (val: string) => void = () => {};
  private onTouched: () => void = () => {};

  constructor(private el: ElementRef) {}

  ngAfterViewInit() {
    this.fpInstance = flatpickr(this.el.nativeElement, {
      enableTime: true,
      dateFormat: "Y-m-d h:i K",
      minDate: "today",
      onChange: (selectedDates: Date[], dateStr: string) => {
        this.onChange(dateStr);
      },
      onClose: () => {
        this.onTouched();
      }
    });
    
    if (this.pendingValue && this.fpInstance) {
      this.fpInstance.setDate(this.pendingValue);
    }
  }

  ngOnDestroy() {
    if (this.fpInstance) {
      this.fpInstance.destroy();
    }
  }

  writeValue(value: any): void {
    if (this.fpInstance) {
      this.fpInstance.setDate(value || '');
    } else {
      this.pendingValue = value || '';
    }
  }

  registerOnChange(fn: any): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: any): void {
    this.onTouched = fn;
  }
}
