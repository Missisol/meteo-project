const pathname = document.location.pathname
const href = document.location.pathname
const items = Array.from(document.querySelectorAll('.nav__item'))

const colorScheme = document.querySelector('meta[name=color-scheme]');
const switchButtons = document.querySelectorAll('.theme-switcher__button');

const nested = document.querySelector('#menu-dropdown')
const navButton = document.querySelector('.nav__button')

const menuToggle = document.querySelector('.menu-toggle');
const menuClose = document.querySelector('.menu-close');
const mobileMenu = document.querySelector('#mobile-menu');
const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');

items.forEach((item) => {
    const a = `/${item.dataset.url.split('.')[1]}`
    if (a === href || (a === '/index' && (href === '/home' || href === '/'))) {
        item.classList.add('active')
    } else {
        item.classList.remove('active')
    }
})

document.body.addEventListener('click', (e) => {
    if (nested.classList.contains('open')) {
        nested.classList.remove('open')
        navButton.setAttribute('aria-expanded', false)
    } else if (e.target === navButton && !nested.classList.contains('open')) {
        nested.classList.add('open')
        navButton.setAttribute('aria-expanded', true)
    }
})

menuToggle.addEventListener('click', () => {
    mobileMenu.classList.add('open')
    mobileMenuOverlay.classList.add('active')
    menuToggle.setAttribute('aria-expanded', true)
})

menuClose.addEventListener('click', () => {
    mobileMenu.classList.remove('open')
    mobileMenuOverlay.classList.remove('active')
    menuToggle.setAttribute('aria-expanded', false)
})

mobileMenuOverlay.addEventListener('click', () => {
    mobileMenu.classList.remove('open')
    mobileMenuOverlay.classList.remove('active')
    menuToggle.setAttribute('aria-expanded', false)
})

switchButtons.forEach((button) => {
	button.addEventListener('click', () => {
		const currentButton = button
        localStorage.setItem('scheme', button.value)
		switchButtons.forEach((button) => button.setAttribute(
				'aria-pressed', button === currentButton
			)
		)
		colorScheme.content = button.value
	})
})

function initScheme() {
    const val = localStorage.getItem('scheme')
    switchButtons.forEach((button) => {
        if (!val) {
            colorScheme.content = 'light dark'
            localStorage.setItem('scheme', 'light dark')
            button.setAttribute('aria-pressed', button.value === 'light dark')
        } else {
            colorScheme.content = val
            button.setAttribute('aria-pressed', val === button.value) 
        }
    })
}

initScheme()