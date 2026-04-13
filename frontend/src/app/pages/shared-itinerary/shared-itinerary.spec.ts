import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SharedItinerary } from './shared-itinerary';

describe('SharedItinerary', () => {
  let component: SharedItinerary;
  let fixture: ComponentFixture<SharedItinerary>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SharedItinerary]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SharedItinerary);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
