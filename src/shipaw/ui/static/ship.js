/**
 * @typedef {Object} Contact
 * @property {string} ContactName
 * @property {string} EmailAddress
 * @property {string} MobilePhone
 */
/**
 * @typedef {Object} Address
 * @property {string} BusinessName
 * @property {string[]} AddressLines
 * @property {string} Town
 * @property {string} Postcode
 * @property {string} [Country = 'GB']
 */
/**
 * @typedef {Object} AddrChoice
 * @property {Address} Address
 * @property {Number} Score
 */

/**
 * @typedef {Object} FullContact
 * @property {Contact} Contact
 * @property {Address} Address
 */

/**
 * @typedef {Object} Shipment
 * @property {FullContact} Recipient
 * @property {FullContact} [Sender]
 * @property {number} Boxes
 * @property {string} ShippingDate
 * @property {string} Reference
 * @property {string} SpecialInstructions1
 * @property {string} SpecialInstructions2
 * @property {string} SpecialInstructions3
 * @property {Object} Context
 * @property {string} Direction
 */

/**
 * @typedef {Object} ShipmentRequest
 * @property {Shipment} Shipment
 * @property {string} ProviderName
 * @property {string} ServiceCode
 *
 */


// FILL FORM FROM CONTEXT
/**
 * Initialize the ship form with shipment data.
 * @param {Shipment} shipment - The shipment data.
 */
async function initShipForm(shipment) {
    console.log('Initializing ship form with shipment:', shipment);
    populateShipment(shipment);
    await populateProviderDropdown();
    const contextjson = JSON.stringify(shipment.Context);
    await setContextJson(contextjson);
    await setAddrChoices();
    await providerChange()
    // setProvider();
    // checkToggleOwnLabel();
    // toggleCollectionTimes();
}

async function setContextJson(contextJson) {
    const contextJsonInput = document.querySelector('input[name="context_json"]');
    contextJsonInput.value = contextJson;
    console.log('contextJsonInput.value', contextJsonInput.value);

}


/**
 * Populates form fields with shipment data.
 // * @param {Shipment} shipment - The shipment data in snake_case.
 */
function populateShipment(shipment) {
    console.log('Populating form from shipment');

    document.getElementById('ship_date').value = shipment.ShippingDate;
    document.getElementById('boxes').value = shipment.Boxes || 1;
    document.getElementById('reference').value = shipment.Reference || "";
    document.getElementById('business_name').value = shipment.Recipient.Address.BusinessName || "";
    document.getElementById('contact_name').value = shipment.Recipient.Contact.ContactName || "";
    document.getElementById('email').value = shipment.Recipient.Contact.EmailAddress || "";
    document.getElementById('mobile_phone').value = shipment.Recipient.Contact.MobilePhone || "";
    document.getElementById('address_line1').value = shipment.Recipient.Address.AddressLines[0] || "";
    document.getElementById('address_line2').value = shipment.Recipient.Address.AddressLines[1] || "";
    document.getElementById('address_line3').value = shipment.Recipient.Address.AddressLines[2] || "";
    document.getElementById('town').value = shipment.Recipient.Address.Town || "";
    document.getElementById('postcode').value = shipment.Recipient.Address.Postcode || "";
}


function toggleDiv(idToToggle, toggleOn) {
    let elementToToggle = document.getElementById(idToToggle);
    if (toggleOn) {
        console.log(`Showing ${idToToggle}`);
        elementToToggle.style.opacity = '100';
    } else {
        console.log(`Hiding ${idToToggle}`);
        elementToToggle.style.opacity = '0'
    }

}


async function providerChange() {
    console.log('Provider changed, updating dependent fields');
    await Promise.all([
        populateServicesDropdown(),
        populateDirectionsDropdown()
    ]);
}

// GATHER FORM DATA
async function contactFromForm() {
    return {
        ContactName: document.getElementById('contact_name').value,
        EmailAddress: document.getElementById('email').value,
        MobilePhone: document.getElementById('mobile_phone').value,
    };
}

async function addressFromForm() {
    return {
        AddressLines: [document.getElementById('address_line1').value, document.getElementById('address_line2').value, document.getElementById('address_line3').value].filter(line => line),
        Town: document.getElementById('town').value,
        Postcode: document.getElementById('postcode').value,
        BusinessName: document.getElementById('business_name').value || "",
    };
}

/**
 * Returns a Contact object.
 * @returns {Shipment}
 */
async function shipmentFromForm() {
    const contactPromise = contactFromForm();
    const addressPromise = addressFromForm();

    // Wait for both to finish
    const [Contact, Address] = await Promise.all([contactPromise, addressPromise]);
    return {
        Recipient: {Contact, Address},
        Boxes: parseInt(document.getElementById('boxes').value, 10) || 1,
        ShippingDate: document.getElementById('ship_date').value,
        Direction: document.getElementById('direction').value || "out",
        Reference: document.getElementById('reference').value || "",
    };
}

/**
 * Returns a Contact object.
 * @returns {ShipmentRequest}
 */
async function shipmentRequestFromForm() {
    return {
        Shipment: await shipmentFromForm(),
        ProviderName: document.getElementById('provider_name').value,
        ServiceCode: document.getElementById('service').value
    }
}


// API Requests
// Provider Specific
async function getJson(url) {
    try {
        const response = await fetch(url, {
            method: 'GET', headers: {'Content-Type': 'application/json'}
        });
        return await response.json();
    } catch (error) {
        console.error('Error fetching json:', error);
    }
}


async function populateDropdown(select, items) {
    select.innerHTML = ''; // Clear existing options
    Object.entries(items).forEach(([key, value]) => {
        const option = document.createElement('option');
        option.textContent = key;
        option.value = String(value);
        select.appendChild(option);
    });
}

async function providerDirectionServices(provider_name) {
    const url = `/provider_direction_services/${provider_name}`;
    const directionServices = await getJson(url);
    const directionsSelect = document.getElementById('direction');
    const directions = Object.keys(directionServices);
    await populateDropdown(directionsSelect, directions);
}

async function getPopulateDropdown(element_id, url) {
    const select = document.getElementById(element_id);
    const items = await getJson(url);
    await populateDropdown(select, items);
}


async function populateProviderDropdown() {
    const url = `api/providers`;
    await getPopulateDropdown('provider_name', url);
}

async function populateDirectionsDropdown() {
    const element = 'direction';
    const provider_name = document.getElementById('provider_name').value;
    const url = `api/provider_directions/${provider_name}`;
    await getPopulateDropdown(element, url);
}


async function populateServicesDropdown() {
    const element_id = 'service';
    const provider_name = document.getElementById('provider_name').value;
    const url = `api/provider_services/${provider_name}`;
    await getPopulateDropdown(element_id, url);
}

// ADDRESS CHOICES / CANDIDATE LOOKUP
async function setAddrChoices() {
    const address = await addressFromForm();
    console.log('Loading AddressChoices for address:', address);
    try {
        const addrChoicesJson = await fetchAddrChoices(address.Postcode, address);
        if (Array.isArray(addrChoicesJson)) {
            await handleAddrChoices(addrChoicesJson);
        }
    } catch (error) {
        console.error('Error fetching AddressChoices:', error);

    }

}

/**
 * Get AddressChoices from server.
 * @param {String} Postcode
 * @param {Address} Address - The address to search.
 * @returns {Promise<AddrChoice[]>}
 */
async function fetchAddrChoices(Postcode, Address) {
    const addrChoiceUrl = 'api/addr_choices';
    console.log(`Posting to ${addrChoiceUrl} pc=${Postcode}, add=${Address}`);
    try {
        const response = await fetch(addrChoiceUrl, {
            method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({
                postcode: Postcode, address: Address
            })
        });
        return await response.json();
    } catch (error) {
        console.error('Error fetching candidates:', error);
    }
}


/**
 * Handles AddressChoices from server.
 * @param {AddrChoice[]} addrChoices
 */
async function handleAddrChoices(addrChoices) {
    console.log('HANDLING ADDR CHOICES', addrChoices);
    let highestScoreOption = null;
    let highestScore = -Infinity;
    const addressSelect = document.getElementById('address-select');
    addressSelect.innerHTML = '';

    for (const choice of addrChoices) {
        const option = await addrChoiceOption(choice);
        if (choice.Score > highestScore) {
            highestScore = choice.Score;
            highestScoreOption = option;
        }
        addressSelect.appendChild(option);
    }

    if (highestScoreOption) {
        console.log('Match Score', highestScore, '%', highestScoreOption.value);
        highestScoreOption.selected = true;
        await setScoreSpan(highestScoreOption);
    }
}

/**
 * Create an option element for an AddressChoice.
 * @param {AddrChoice} addressChoice
 * @returns {HTMLOptionElement}
 */
async function addrChoiceOption(addressChoice) {
    const option = document.createElement('option');
    option.value = JSON.stringify(addressChoice.Address);
    option.textContent = await addressLinesOutput(addressChoice.Address, ', ');
    option.dataset.score = addressChoice.Score.toString();
    return option;
}

// UPDATE FORM
/**
 * Update address fields with given address data.
 * @param {Address} Address
 */
function updateAddressFields(Address) {
    console.log('Updating manual fields');
    document.getElementById('address_line1').value = Address.AddressLines[0] || '';
    document.getElementById('address_line2').value = Address.AddressLines?.[1] || '';
    document.getElementById('address_line3').value = Address.AddressLines?.[2] || '';
    document.getElementById('town').value = Address.Town || '';
    document.getElementById('postcode').value = Address.Postcode || '';
}

async function updateAddressFromSelect() {
    const selectedOption = document.getElementById('address-select').value;
    updateAddressFieldsFromJson(selectedOption);
}

function updateAddressFieldsFromJson(address_json) {
    const address = JSON.parse(address_json);
    updateAddressFields(address);
}

async function scoreCssSelector(score) {
    if (score > 80) return 'high-score';
    if (score >= 60) return 'medium-score';
    return 'low-score';
}


async function setScoreSpan(option) {
    const scoreSpan = document.getElementById('score-span');
    const address = JSON.parse(option.value);
    const score = parseInt(option.dataset.score, 10) || 0;
    const addressHtml = await addressLinesOutput(address, '<br>');

    scoreSpan.className = await scoreCssSelector(score);
    scoreSpan.innerHTML = `Best Guess (click to insert)<br>${addressHtml}`;
    scoreSpan.onclick = await updateAddressFromSelect;
}

async function addressLinesOutput(Address, Seperator) {
    return (await getAddressLines(Address)).join(Seperator);
}

/**
 * Get non-empty address lines from Address object.
 * @param {Address} Address
 * @returns {Promise[string[]]}}
 */
async function getAddressLines(Address) {
    return [...Address.AddressLines]
        .filter(line => line);
}

// force make small after selection
document.addEventListener('DOMContentLoaded', function () {
    const serviceSelect = document.getElementById('service');
    serviceSelect.addEventListener('change', function () {
        this.blur();
    });

});


async function logShipreq() {
    const shipreq = await shipmentRequestFromForm();
    console.log("SHIPREQ FROM FORM", shipreq);
}