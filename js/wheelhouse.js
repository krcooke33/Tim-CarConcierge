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
      examples: "'68 Mustangs, early Broncos, 911 long-hood, 280SL.",
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
      photo: {
        src: '/img/gallery/porsche-911.jpg',
        alt: 'Red Porsche 911, front three-quarter view in a parking lot',
        width: 800,
        height: 600
      }
    }
  ];

  function buildEra(era, includePhoto) {
    var li = document.createElement('li');
    li.className = 'wheelhouse-era';

    if (includePhoto && era.photo) {
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
    name.textContent = era.name;
    li.appendChild(name);

    var examples = document.createElement('p');
    examples.className = 'era-examples';
    examples.textContent = era.examples;
    li.appendChild(examples);

    return li;
  }

  function render() {
    var lists = document.querySelectorAll('[data-wheelhouse]');
    if (!lists.length) return;

    lists.forEach(function (list) {
      var includePhoto = list.getAttribute('data-variant') === 'process';
      list.innerHTML = '';
      ERAS.forEach(function (era) {
        list.appendChild(buildEra(era, includePhoto));
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', render);
  } else {
    render();
  }
})();
