/**
 * @typedef {Object} Contact
 * @property {string} Name
 * @property {string} Address
 * @property {string} Phone
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
 * @typedef {Object} AddrSummary
 * @property {string} addressId
 * @property {string} type
 * @property {string} addressSummary1
 * @property {string} addressSummary2
 * @property {string} highlight
 */

/**
 * @typedef {Object} AddressRecord
 * @property {string} AddressId
 * @property {string} DomesticId
 * @property {string} Language
 * @property {string} LanguageAlternatives
 * @property {string} Department
 * @property {string} Company
 * @property {string} SubBuilding
 * @property {string} BuildingNumber
 * @property {string} BuildingName
 * @property {string} SecondaryStreet
 * @property {string} Street
 * @property {string} Block
 * @property {string} Neighbourhood
 * @property {string} District
 * @property {string} City
 * @property {string} Line1
 * @property {string} Line2
 * @property {string} Line3
 * @property {string} Line4
 * @property {string} Line5
 * @property {string} AdminAreaName
 * @property {string} AdminAreaCode
 * @property {string} Province
 * @property {string} ProvinceName
 * @property {string} ProvinceCode
 * @property {string} PostalCode
 * @property {string} CountryName
 * @property {string} CountryIso2
 * @property {string} CountryIso3
 * @property {string} CountryIsoNumber
 * @property {string} SortingNumber1
 * @property {string} SortingNumber2
 * @property {string} Barcode
 * @property {string} PoBoxNumber
 * @property {string} Label
 * @property {string} Type
 * @property {string} DataLevel
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
 */


// FILL FORM FROM CONTEXT
/**
 * Initialize the ship form with shipment data.
 * @param {Shipment} shipment - The shipment data.
 */
async function initShipForm(shipment) {
    console.log('Initializing ship form with shipment:', shipment);
    populateShipment(shipment);

    const providerNames = await getJson(`api/providers`);
    await populateDropdown('provider_name', providerNames);

    const contextjson = JSON.stringify(shipment.Context);
    await setContextJson(contextjson);
    await setAddrChoicesFull();
    await providerChanged()
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
    document.getElementById('contact_name').value = shipment.Recipient.Contact.Name || "";
    document.getElementById('email').value = shipment.Recipient.Contact.Email || "";
    document.getElementById('mobile_phone').value = shipment.Recipient.Contact.Phone || "";
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

async function populateDropdown(selectId, items) {
    const select = document.getElementById(selectId);
    select.innerHTML = ''; // Clear existing options
    Object.entries(items).forEach(([key, value]) => {
        const option = document.createElement('option');
        option.textContent = key;
        option.value = String(value);
        select.appendChild(option);
    });
}

async function changeProvider(providerName) {
    console.log('changeProvider', providerName);
    const providerDirections = await getJson(`api/provider_directions/${providerName}`);
    await populateDropdown('direction', providerDirections);
    const direction = document.getElementById('direction').value;

}

async function providerChanged() {
    console.log('providerChanged');
    const provider_name = document.getElementById('provider_name').value;
    console.log('Selected provider:', provider_name);
    await changeProvider(provider_name);
    const direction = document.getElementById('direction').value;
    await changeDirection(provider_name, direction);
}


async function changeDirection(providerName, direction) {
    console.log('changeDirection', providerName, direction);
    const services = await getJson(`api/provider_direction_services/${providerName}/${direction}`);
    await populateDropdown('service', services);
    // const formats = await getJson(`api/provider_direction_formats/${providerName}/${direction}`);
    // console.log('Received formats:', formats);
    // await populateDropdown('package_format', formats);
}

async function directionChanged() {
    console.log('directionChanged');
    const provider_name = document.getElementById('provider_name').value;
    const direction = document.getElementById('direction').value;
    await changeDirection(provider_name, direction);
}


// GATHER FORM DATA
async function contactFromForm() {
    console.log('contactFromForm');
    return {
        Name: document.getElementById('contact_name').value,
        Email: document.getElementById('email').value,
        Phone: document.getElementById('mobile_phone').value,
    };
}

async function addressFromForm() {
    console.log('addressFromForm');
    return {
        AddressLines: [document.getElementById('address_line1').value, document.getElementById('address_line2').value, document.getElementById('address_line3').value].filter(line => line),
        Town: document.getElementById('town').value,
        Postcode: document.getElementById('postcode').value,
        BusinessName: document.getElementById('business_name').value || "",
    };
}

// API Requests
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


// ADDRESS CHOICES / CANDIDATE LOOKUP

async function setAddrChoicesFull() {
    const address = await addressFromForm();
    console.log('Loading AddressChoices for address:', address);
    try {
        const addrRecordChoices = await fetchAddrRecordsFull(address);
        if (Array.isArray(addrRecordChoices)) {
            await handleAddrRecordChoices(addrRecordChoices);
        }
    } catch (error) {
        console.error('Error fetching AddressChoices:', error);

    }

}



async function fetchAddrRecordsFull(address) {
    const addrSearchUrl = `api/address_search_full`;
    try {
        const response = await fetch(addrSearchUrl, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(address)
        })
        return await response.json();
    } catch (error) {
        console.error('Error fetching candidates:', error);
    }
}


async function handleAddrRecordChoices(addrRecords) {
    console.log('Handling address record choices:', addrRecords);
    const addressSelect = document.getElementById('address-select');
    addressSelect.innerHTML = ''; // Clear existing options
    for (const choice of addrRecords) {
        const option = await addrRecordOption(choice);
        addressSelect.appendChild(option);
    }
}


async function addrRecordOption(addressRecord) {
    console.log('Creating option for address record:', addressRecord);
    const option = document.createElement('option');
    option.value = addressRecord.addressId;
    option.textContent = addressRecord.Label;
    return option;
}

// UPDATE FORM
/**
 * Update address fields with given address data.
 * @param {AddressRecord} addressRecord
 */
function updateAddressFields(addressRecord) {
    console.log(`Updating manual fields with address record:`, addressRecord);
    document.getElementById('address_line1').value = addressRecord.Line1 || '';
    document.getElementById('address_line2').value = addressRecord.Line2 || '';
    document.getElementById('address_line3').value = addressRecord.Line3 || '';
    document.getElementById('town').value = addressRecord.City || '';
    document.getElementById('postcode').value = addressRecord.PostalCode || '';
    if (addressRecord.Company) {
        document.getElementById('business_name').value = addressRecord.Company;
    }
}

async function updateAddressFromSelect() {
    console.log('Address select changed, updating address fields');
    const selectedAddrID = document.getElementById('address-select').value;
    console.log('Selected address ID:', selectedAddrID);
    if (!selectedAddrID) {
        console.warn('Address ID is empty (i.e. was street etc) , skipping address update.');
        return;
    }
    const addressRecord = await getJson(`api/address_retrieve/${encodeURIComponent(selectedAddrID)}`);
    console.log('Retrieved address JSON:', addressRecord);
    updateAddressFields(addressRecord);
}

// force make small after selection
document.addEventListener('DOMContentLoaded', function () {
    const serviceSelect = document.getElementById('service');
    serviceSelect.addEventListener('change', function () {
        this.blur();
    });

});


// legacy

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


// async function logShipreq() {
//     const shipreq = await shipmentRequestFromForm();
//     console.log("SHIPREQ FROM FORM", shipreq);
// }


// LEGACY


// async function setAddrChoices() {
//     console.log('Setting address choices');
//     const address = await addressFromForm();
//     // const searchText = address.Postcode || address.AddressLines[0] || "";
//     const searchText = [address?.AddressLines?.[0] || '', address?.AddressLines?.[1] || '', address?.Postcode || '']
//         .filter(s => s && s.trim())
//         .join(' ')
//         .trim();
//
//     console.log('Loading AddressChoices for address:', address);
//     try {
//         const addrChoicesJson = await fetchAddrChoices(searchText);
//         if (Array.isArray(addrChoicesJson)) {
//             await handleAddrChoices(addrChoicesJson);
//         }
//     } catch (error) {
//         console.error('Error fetching AddressChoices:', error);
//
//     }
//
// }


// async function fetchAddrChoices(SearchText) {
//     const addrChoiceUrl = `api/address_search/${encodeURIComponent(SearchText)}`;
//     console.log(`Posting searchtext ${SearchText} to ${addrChoiceUrl} `);
//     try {
//         const response = await fetch(addrChoiceUrl, {
//             method: 'GET', headers: {'Content-Type': 'application/json'}
//         })
//         return await response.json();
//     } catch (error) {
//         console.error('Error fetching candidates:', error);
//     }
// }


// async function handleAddrChoices(addrSummaries) {
//     const addressSelect = document.getElementById('address-select');
//     for (const choice of addrSummaries) {
//         const option = await addrChoiceOption(choice);
//         addressSelect.appendChild(option);
//     }
// }


//
// async function addrChoiceOption(addressSummary) {
//     const option = document.createElement('option');
//     if (addressSummary.type === 'Address') {
//         option.value = addressSummary.addressId;
//     } else {
//         option.value = '';
//     }
//     option.textContent = addressSummary.addressSummary1 + ', ' + addressSummary.addressSummary2;
//     return option;
// }


// /**
//  * @returns {Shipment}
//  */
// async function shipmentFromForm() {
//     const contactPromise = contactFromForm();
//     const addressPromise = addressFromForm();
//
//     // Wait for both to finish
//     const [Contact, Address] = await Promise.all([contactPromise, addressPromise]);
//     return {
//         Recipient: {Contact, Address},
//         Boxes: parseInt(document.getElementById('boxes').value, 10) || 1,
//         ShippingDate: document.getElementById('ship_date').value,
//         Direction: document.getElementById('direction').value || "out",
//         Reference: document.getElementById('reference').value || "",
//     };
// }


// async function fetchAddrRecords(postcode, searchText) {
//     const params = new URLSearchParams({postcode, search_text: searchText});
//     const addrChoiceUrl = `api/address_search_pc?${params.toString()}`;
//     // const addrChoiceUrl = `api/address_search_pc/${encodeURIComponent(postcode)}/${encodeURIComponent(searchText)}`;
//     try {
//         const response = await fetch(addrChoiceUrl, {
//             method: 'GET', headers: {'Content-Type': 'application/json'}
//         })
//         return await response.json();
//     } catch (error) {
//         console.error('Error fetching candidates:', error);
//     }
// }