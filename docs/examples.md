# Examples

This section provides practical examples for common use cases with OpenAstro2.

## Basic Examples

### Simple Natal Chart

```python
from openastro2.openastro2 import openAstro

# Create birth event
birth = openAstro.event(
    name="Albert Einstein",
    year=1879, month=3, day=14,
    hour=11, minute=30, second=0,
    timezone=1,  # UTC+1
    location="Ulm, Germany",
    geolat=48.4011, geolon=9.9876
)

# Generate natal chart
natal_chart = openAstro(birth, type="Radix")

# Save as SVG
svg_content = natal_chart.makeSVG2()
with open("einstein_natal.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)

# Print basic information
print(f"Sun sign: {natal_chart.planets_sign[0]}")  # 0 = Aries, 1 = Taurus, etc.
print(f"Moon sign: {natal_chart.planets_sign[1]}")
print(f"Ascendant: {natal_chart.houses_degree_ut[0]:.2f}°")
```

### Current Transits

```python
from datetime import datetime
import pytz

# Get current transits for Einstein's chart
def get_current_transits(natal_event):
    # Create current moment event
    now = datetime.now(pytz.UTC)
    
    current_event = openAstro.event_dt_str(
        name="Current Transits",
        dt_str=now.strftime("%Y-%m-%d %H:%M:%S"),
        timezone=0,  # UTC
        location=natal_event["location"],
        geolat=natal_event["geolat"],
        geolon=natal_event["geolon"]
    )
    
    # Create transit chart
    transit_chart = openAstro(natal_event, current_event, type="Transit")
    return transit_chart

transits = get_current_transits(birth)
```

## Advanced Examples

### Multi-Chart Analysis

```python
class AstrologicalProfile:
    """Complete astrological analysis for a person."""
    
    def __init__(self, name, birth_data):
        self.name = name
        self.birth_event = openAstro.event(**birth_data)
        self.charts = {}
        
    def generate_all_charts(self):
        """Generate comprehensive chart set."""
        
        # Core charts
        self.charts['natal'] = openAstro(self.birth_event, type="Radix")
        self.charts['current_transits'] = openAstro(self.birth_event, type="Transit")
        self.charts['progressions'] = openAstro(self.birth_event, type="SProgression")
        
        # Return charts
        self.charts['solar_return'] = openAstro(self.birth_event, type="Solar")
        self.charts['lunar_return'] = openAstro(self.birth_event, type="Lunar")
        
        # Lunation charts
        self.charts['new_moon'] = openAstro(self.birth_event, type="NewMoonNext")
        self.charts['full_moon'] = openAstro(self.birth_event, type="FullMoonNext")
        
    def get_planet_positions(self, chart_type='natal'):
        """Extract planet positions from specified chart."""
        chart = self.charts.get(chart_type)
        if not chart:
            return None
            
        planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
                  'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        positions = {}
        for i, planet in enumerate(planets):
            if i < len(chart.planets_degree_ut):
                positions[planet] = {
                    'degree': chart.planets_degree_ut[i],
                    'sign': signs[chart.planets_sign[i]],
                    'retrograde': bool(chart.planets_retrograde[i])
                }
        
        return positions
    
    def save_all_charts(self, output_dir="charts"):
        """Save all charts as SVG files."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for chart_type, chart in self.charts.items():
            filename = f"{output_dir}/{self.name}_{chart_type}.svg"
            svg_content = chart.makeSVG2()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(svg_content)
                
    def generate_report(self):
        """Generate text report of key information."""
        natal_positions = self.get_planet_positions('natal')
        
        report = f"Astrological Profile: {self.name}\n"
        report += "=" * 50 + "\n\n"
        
        if natal_positions:
            report += "Natal Planet Positions:\n"
            for planet, data in natal_positions.items():
                retro = " (R)" if data['retrograde'] else ""
                report += f"{planet}: {data['degree']:.2f}° {data['sign']}{retro}\n"
        
        return report

# Usage example
birth_data = {
    'name': 'Marie Curie',
    'year': 1867, 'month': 11, 'day': 7,
    'hour': 12, 'minute': 0, 'second': 0,
    'timezone': 1, 'location': 'Warsaw, Poland',
    'geolat': 52.2297, 'geolon': 21.0122
}

profile = AstrologicalProfile("Marie Curie", birth_data)
profile.generate_all_charts()
profile.save_all_charts()
print(profile.generate_report())
```

### Relationship Compatibility

```python
class RelationshipAnalysis:
    """Analyze compatibility between two people."""
    
    def __init__(self, person1_data, person2_data):
        self.person1 = openAstro.event(**person1_data)
        self.person2 = openAstro.event(**person2_data)
        self.person1_name = person1_data['name']
        self.person2_name = person2_data['name']
        
    def create_synastry_charts(self):
        """Create synastry charts (each person's planets in other's chart)."""
        
        # Person 1's planets in Person 2's chart
        synastry_1_to_2 = openAstro(self.person1, self.person2, type="Transit")
        
        # Person 2's planets in Person 1's chart  
        synastry_2_to_1 = openAstro(self.person2, self.person1, type="Transit")
        
        return synastry_1_to_2, synastry_2_to_1
    
    def analyze_sun_moon_connections(self):
        """Analyze Sun-Moon connections between partners."""
        
        chart1 = openAstro(self.person1, type="Radix")
        chart2 = openAstro(self.person2, type="Radix")
        
        # Get positions
        p1_sun = chart1.planets_degree_ut[0]
        p1_moon = chart1.planets_degree_ut[1]
        p2_sun = chart2.planets_degree_ut[0] 
        p2_moon = chart2.planets_degree_ut[1]
        
        connections = {}
        
        # Calculate aspects between Sun/Moon combinations
        def calculate_aspect(pos1, pos2):
            diff = abs(pos1 - pos2)
            if diff > 180:
                diff = 360 - diff
            return diff
        
        connections['p1_sun_p2_moon'] = calculate_aspect(p1_sun, p2_moon)
        connections['p1_moon_p2_sun'] = calculate_aspect(p1_moon, p2_sun)
        connections['p1_sun_p2_sun'] = calculate_aspect(p1_sun, p2_sun)
        connections['p1_moon_p2_moon'] = calculate_aspect(p1_moon, p2_moon)
        
        return connections
    
    def generate_compatibility_report(self):
        """Generate compatibility analysis report."""
        
        sun_moon = self.analyze_sun_moon_connections()
        
        report = f"Relationship Analysis: {self.person1_name} & {self.person2_name}\n"
        report += "=" * 60 + "\n\n"
        
        report += "Sun-Moon Connections:\n"
        for connection, angle in sun_moon.items():
            aspect_type = self.classify_aspect(angle)
            report += f"{connection}: {angle:.2f}° ({aspect_type})\n"
        
        return report
    
    def classify_aspect(self, angle):
        """Classify aspect angle into type."""
        if angle <= 8:
            return "Conjunction"
        elif 52 <= angle <= 68:
            return "Sextile" 
        elif 82 <= angle <= 98:
            return "Square"
        elif 112 <= angle <= 128:
            return "Trine"
        elif 172 <= angle <= 188:
            return "Opposition"
        else:
            return "No major aspect"

# Example usage
person1 = {
    'name': 'John',
    'year': 1985, 'month': 6, 'day': 15,
    'hour': 14, 'minute': 30, 'second': 0,
    'timezone': 2, 'location': 'Berlin',
    'geolat': 52.5200, 'geolon': 13.4050
}

person2 = {
    'name': 'Jane',
    'year': 1987, 'month': 9, 'day': 22,
    'hour': 18, 'minute': 45, 'second': 0,
    'timezone': 2, 'location': 'Berlin',
    'geolat': 52.5200, 'geolon': 13.4050
}

relationship = RelationshipAnalysis(person1, person2)
print(relationship.generate_compatibility_report())
```

### Batch Chart Processing

```python
def batch_process_charts(people_data, chart_types=['Radix'], output_format='svg'):
    """Process multiple charts in batch."""
    
    results = []
    
    for person_data in people_data:
        person_results = {'name': person_data['name'], 'charts': {}}
        
        # Create event
        try:
            event = openAstro.event(**person_data)
        except Exception as e:
            print(f"Error creating event for {person_data['name']}: {e}")
            continue
        
        # Generate requested chart types
        for chart_type in chart_types:
            try:
                chart = openAstro(event, type=chart_type)
                
                if output_format == 'svg':
                    content = chart.makeSVG2()
                    filename = f"{person_data['name']}_{chart_type}.svg"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    person_results['charts'][chart_type] = filename
                
                elif output_format == 'data':
                    # Extract key data points
                    chart_data = {
                        'planets_degrees': chart.planets_degree_ut[:10],  # Main planets
                        'planets_signs': chart.planets_sign[:10],
                        'houses': chart.houses_degree_ut,
                        'lunar_phase': chart.lunar_phase
                    }
                    person_results['charts'][chart_type] = chart_data
                    
            except Exception as e:
                print(f"Error creating {chart_type} for {person_data['name']}: {e}")
                continue
        
        results.append(person_results)
    
    return results

# Example data
people = [
    {
        'name': 'Person1',
        'year': 1990, 'month': 1, 'day': 15,
        'hour': 12, 'minute': 0, 'second': 0,
        'timezone': 0, 'location': 'London',
        'geolat': 51.5074, 'geolon': -0.1278
    },
    {
        'name': 'Person2', 
        'year': 1992, 'month': 6, 'day': 30,
        'hour': 18, 'minute': 30, 'second': 0,
        'timezone': 2, 'location': 'Berlin',
        'geolat': 52.5200, 'geolon': 13.4050
    }
    # Add more people...
]

# Process all charts
results = batch_process_charts(
    people, 
    chart_types=['Radix', 'Solar', 'Transit'],
    output_format='data'
)
```

### Research Data Extraction

```python
from datetime import datetime, timedelta

class AstrologyDataExtractor:
    """Extract astrological data for research purposes."""
    
    def __init__(self, settings=None):
        self.settings = settings or {
            'astrocfg': {
                'houses_system': 'E',  # Equal houses for research
                'postype': 'truegeo',  # True geocentric
                'zodiactype': 'tropical'
            }
        }
    
    def extract_planet_data(self, events):
        """Extract planet positions for multiple events."""
        
        data = []
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        for event_data in events:
            try:
                event = openAstro.event(**event_data)
                chart = openAstro(event, type="Radix", settings=self.settings)
                
                row = {
                    'name': event_data['name'],
                    'date': f"{event_data['year']}-{event_data['month']:02d}-{event_data['day']:02d}",
                    'time': f"{event_data['hour']:02d}:{event_data['minute']:02d}",
                    'location': event_data.get('location', ''),
                    'latitude': event_data.get('geolat', 0),
                    'longitude': event_data.get('geolon', 0)
                }
                
                # Add planet positions
                planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
                          'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
                
                for i, planet in enumerate(planets):
                    if i < len(chart.planets_degree_ut):
                        row[f'{planet}_degree'] = chart.planets_degree_ut[i]
                        row[f'{planet}_sign'] = signs[chart.planets_sign[i]]
                        row[f'{planet}_sign_num'] = chart.planets_sign[i]
                        row[f'{planet}_retrograde'] = chart.planets_retrograde[i]
                
                # Add house positions
                for i in range(12):
                    if i < len(chart.houses_degree_ut):
                        row[f'House_{i+1}_cusp'] = chart.houses_degree_ut[i]
                
                # Add lunar phase
                if hasattr(chart, 'lunar_phase'):
                    row['lunar_phase_degrees'] = chart.lunar_phase.get('degrees', 0)
                    row['lunar_phase_name'] = chart.lunar_phase.get('moon_phase', '')
                
                data.append(row)
                
            except Exception as e:
                print(f"Error processing {event_data.get('name', 'Unknown')}: {e}")
                continue
        
        return data
    
    def analyze_element_distribution(self, rows):
        """Analyze distribution of planets by element."""
        
        element_map = {
            0: 'Fire', 1: 'Earth', 2: 'Air', 3: 'Water',    # Aries, Taurus, Gemini, Cancer
            4: 'Fire', 5: 'Earth', 6: 'Air', 7: 'Water',    # Leo, Virgo, Libra, Scorpio  
            8: 'Fire', 9: 'Earth', 10: 'Air', 11: 'Water'   # Sagittarius, Capricorn, Aquarius, Pisces
        }
        
        planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
                  'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
        
        element_counts = {'Fire': 0, 'Earth': 0, 'Air': 0, 'Water': 0}
        
        for planet in planets:
            sign_col = f'{planet}_sign_num'
            for row in rows:
                sign_num = row.get(sign_col)
                if sign_num is None:
                    continue
                element = element_map.get(sign_num, 'Unknown')
                if element in element_counts:
                    element_counts[element] += 1
        
        return element_counts
    
    def find_aspect_patterns(self, rows, aspect_orb=8):
        """Find common aspect patterns in dataset."""
        
        patterns = []
        
        for row in rows:
            row_patterns = []
            
            # Check major aspects between planets
            planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars']
            
            for i, planet1 in enumerate(planets):
                for j, planet2 in enumerate(planets[i+1:], i+1):
                    p1_col = f'{planet1}_degree'
                    p2_col = f'{planet2}_degree'
                    
                    if p1_col in row and p2_col in row:
                        diff = abs(row[p1_col] - row[p2_col])
                        if diff > 180:
                            diff = 360 - diff
                        
                        # Check for major aspects
                        if abs(diff - 0) <= aspect_orb:
                            row_patterns.append(f'{planet1}-{planet2} Conjunction')
                        elif abs(diff - 90) <= aspect_orb:
                            row_patterns.append(f'{planet1}-{planet2} Square')
                        elif abs(diff - 120) <= aspect_orb:
                            row_patterns.append(f'{planet1}-{planet2} Trine')
                        elif abs(diff - 180) <= aspect_orb:
                            row_patterns.append(f'{planet1}-{planet2} Opposition')
            
            patterns.append({
                'name': row.get('name', ''),
                'patterns': row_patterns
            })
        
        return patterns

# Example usage for research
research_events = [
    # Add your research subjects here
    {
        'name': 'Subject1',
        'year': 1990, 'month': 3, 'day': 21,
        'hour': 12, 'minute': 0, 'second': 0,
        'timezone': 0, 'location': 'London',
        'geolat': 51.5074, 'geolon': -0.1278
    },
    # ... more subjects
]

extractor = AstrologyDataExtractor()
df = extractor.extract_planet_data(research_events)
element_dist = extractor.analyze_element_distribution(df)
patterns = extractor.find_aspect_patterns(df)

# Save research data
df.to_csv('astrology_research_data.csv', index=False)
print("Element distribution:", element_dist)
```

### Transit Tracking

```python
from datetime import datetime, timedelta
import json

class TransitTracker:
    """Track important transits over time."""
    
    def __init__(self, natal_event):
        self.natal_event = natal_event
        self.natal_chart = openAstro(natal_event, type="Radix")
    
    def track_transits_for_period(self, start_date, end_date, step_days=1):
        """Track transits over a specified period."""
        
        current_date = start_date
        transit_data = []
        
        while current_date <= end_date:
            # Create transit event for current date
            transit_event = openAstro.event_dt_str(
                name="Transit",
                dt_str=current_date.strftime("%Y-%m-%d 12:00:00"),
                timezone=self.natal_event["timezone"],
                location=self.natal_event["location"],
                geolat=self.natal_event["geolat"],
                geolon=self.natal_event["geolon"]
            )
            
            # Create transit chart
            transit_chart = openAstro(self.natal_event, transit_event, type="Transit")
            
            # Extract significant transits
            day_transits = self.find_significant_transits(transit_chart, current_date)
            if day_transits:
                transit_data.extend(day_transits)
            
            current_date += timedelta(days=step_days)
        
        return transit_data
    
    def find_significant_transits(self, transit_chart, date, orb=2):
        """Find significant transits for a given date."""
        
        significant_transits = []
        
        # Get natal positions
        natal_positions = self.natal_chart.planets_degree_ut[:10]  # Main planets
        
        # Get transit positions  
        transit_positions = transit_chart.t_planets_degree_ut[:10] if hasattr(transit_chart, 't_planets_degree_ut') else []
        
        if not transit_positions:
            return significant_transits
        
        planet_names = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
                       'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
        
        # Check for aspects between transiting and natal planets
        for t_idx, t_planet in enumerate(planet_names[:len(transit_positions)]):
            for n_idx, n_planet in enumerate(planet_names[:len(natal_positions)]):
                
                t_pos = transit_positions[t_idx]
                n_pos = natal_positions[n_idx]
                
                diff = abs(t_pos - n_pos)
                if diff > 180:
                    diff = 360 - diff
                
                # Check for major aspects
                aspect = None
                if abs(diff - 0) <= orb:
                    aspect = "Conjunction"
                elif abs(diff - 90) <= orb:
                    aspect = "Square"
                elif abs(diff - 120) <= orb:
                    aspect = "Trine"
                elif abs(diff - 180) <= orb:
                    aspect = "Opposition"
                
                if aspect:
                    significant_transits.append({
                        'date': date.strftime("%Y-%m-%d"),
                        'transit_planet': t_planet,
                        'natal_planet': n_planet,
                        'aspect': aspect,
                        'orb': min(abs(diff - 0), abs(diff - 90), 
                                  abs(diff - 120), abs(diff - 180)),
                        'description': f"Transiting {t_planet} {aspect} Natal {n_planet}"
                    })
        
        return significant_transits
    
    def get_upcoming_transits(self, days_ahead=30):
        """Get upcoming significant transits."""
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_ahead)
        
        return self.track_transits_for_period(start_date, end_date)
    
    def save_transit_report(self, transits, filename):
        """Save transit report to JSON file."""
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(transits, f, indent=2, ensure_ascii=False)

# Example usage
birth_event = openAstro.event(
    "Sample Person", 1990, 6, 15, 14, 30, 0,
    timezone=2, location="Berlin",
    geolat=52.5200, geolon=13.4050
)

tracker = TransitTracker(birth_event)
upcoming = tracker.get_upcoming_transits(60)  # Next 60 days
tracker.save_transit_report(upcoming, "upcoming_transits.json")

for transit in upcoming[:5]:  # Show first 5
    print(f"{transit['date']}: {transit['description']}")
```

These examples demonstrate how to use OpenAstro2 for various practical applications, from simple chart creation to complex research and analysis tasks.
