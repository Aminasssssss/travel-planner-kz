import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ItineraryAnalysis } from './itinerary-analysis';

describe('ItineraryAnalysis', () => {
  let component: ItineraryAnalysis;
  let fixture: ComponentFixture<ItineraryAnalysis>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ItineraryAnalysis]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ItineraryAnalysis);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
