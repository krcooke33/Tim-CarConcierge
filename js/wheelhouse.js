/* wheelhouse.js — single source of truth for the four eras
   ─────────────────────────────────────────────────────────
   The Home (`/`) and Process (`/process/`) pages both display
   the same four wheelhouse eras (year range, name, example cars).
   Defining them here once prevents the two lists from drifting
   out of sync when Tim updates an example car.

   Each page includes an empty placeholder:
     <ol class="wheelhouse-grid" data-wheelhouse data-variant="home"></ol>
     <ol class="wheelhouse-grid" data-wheelhouse data-variant="process"></ol>

   The "process" variant renders an era photo at the top of
   each card; the "home" variant is text-only.                */

(function () {
  var ERAS = [
    {
      range: '1966–1974',
      name: 'Muscle & Originals',
      // Short list — used on Home (compact, taste-only)
      examples: "'68 Mustangs, early Broncos, 911 long-hood, 280SL.",
      // Long-form description + longer car list — used on /process/
      description: 'American muscle, early SUVs, and the European sports cars that defined the era.',
      examplesLong: 'Mustang, Camaro, Charger, early Bronco, FJ40, 911 long-hood, Mercedes 280SL Pagoda, Alfa Spider, Ferrari 246 Dino, Jaguar E-Type.',
      photo: {
        src: '/img/gallery/ford-bronco.jpg',
        alt: 'Burnt-orange first-generation Ford Bronco with white roof, parked on a paved drive',
        width: 800,
        height: 600
      }
    },
    {
      range: '1975–1984',
      name: 'Malaise & Survivors',
      examples: 'R107 SLs, BMW E9 / E24, 911 SC, Alfa GTV6.',
      description: 'Detroit stumbled. The Europeans and Japanese kept building interesting cars.',
      examplesLong: '911 SC, 930 Turbo, Mercedes R107 SL, BMW E24, Alfa GTV6, Ferrari 308, early RX-7, 280Z.',
      photo: {
        src: '/img/gallery/mercedes-450sl.jpg',
        alt: 'Dark blue Mercedes-Benz 450SL (R107) with hardtop, parked in a driveway',
        width: 800,
        height: 600
      }
    },
    {
      range: '1985–1994',
      name: 'Analog Modern',
      examples: 'E30, 964, R32 Skyline, Supra MkIII, NSX.',
      description: 'Engineered to perform, not yet managed by software.',
      examplesLong: 'E30 M3, Porsche 964, Honda NSX, R32 Skyline GT-R, Lancia Delta Integrale, Ferrari 328, Miata NA, BMW E34 M5.',
      photo: {
        src: '/img/gallery/bmw-e30-touring.jpg',
        alt: 'Red BMW E30 Touring wagon with roof rack, parked at the curb',
        width: 800,
        height: 600
      }
    },
    {
      range: '1995–1999',
      name: 'BaT Era',
      examples: 'E36 M3, 993, 80-Series Land Cruiser, Integra Type R.',
      description: "Yesterday's used car. Today's auction darling.",
      examplesLong: 'Porsche 993, E36 M3, Integra Type R, Supra MkIV, Land Cruiser 80-series, Ferrari F355, BMW E39 M5, Dodge Viper.',
      photo: {
        src: '/img/gallery/porsche-911.jpg',
        alt: 'Red Porsche 911, front three-quarter view in a parking lot',
        width: 800,
        height: 600
      }
    }
  ];

  function buildEra(era, variant) {
    var li = document.createElement('li');
    li.className = 'wheelhouse-era';

    if (variant === 'process' && era.photo) {
      var img = document.createElement('img');
      img.className = 'era-photo';
      img.src = era.photo.src;
      img.alt = era.photo.alt;
      img.loading = 'lazy';
      img.width = era.photo.width;
      img.height = era.photo.height;
      li.appendChild(img);
    }

    var range = document.createElement('p');
    range.className = 'era-range';
    range.textContent = era.range;
    li.appendChild(range);

    var name = document.createElement('h3');
    name.className = 'era-name';
    // Use the brand ampersand span so "Muscle & Originals" / "Malaise & Survivors"
    // render with the same pinned-opsz oxblood ampersand as "The & Garage" wordmark,
    // not the Fraunces display-size swash glyph.
    name.innerHTML = era.name.replace(/&/g, '<span class="brand-amp">&amp;</span>');
    li.appendChild(name);

    if (variant === 'process' && era.description) {
      var description = document.createElement('p');
      description.className = 'era-description';
      description.textContent = era.description;
      li.appendChild(description);
    }

    var examples = document.createElement('p');
    examples.className = 'era-examples';
    examples.textContent = (variant === 'process' && era.examplesLong) ? era.examplesLong : era.examples;
    li.appendChild(examples);

    return li;
  }

  function render() {
    var lists = document.querySelectorAll('[data-wheelhouse]');
    if (!lists.length) return;

    lists.forEach(function (list) {
      var variant = list.getAttribute('data-variant') || 'home';
      list.innerHTML = '';
      ERAS.forEach(function (era) {
        list.appendChild(buildEra(era, variant));
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', render);
  } else {
    render();
  }
})();
