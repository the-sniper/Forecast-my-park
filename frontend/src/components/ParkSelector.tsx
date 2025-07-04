"use client";

import { useState, Fragment } from "react";
import {
  Listbox,
  ListboxButton,
  ListboxOptions,
  ListboxOption,
  Transition,
} from "@headlessui/react";
import { ChevronsUpDownIcon, CheckIcon, MapPinIcon } from "lucide-react";
import { Park } from "@/types/forecast";
import { cn } from "@/lib/utils";

interface ParkSelectorProps {
  parks: Park[];
  selectedPark: Park | null;
  onParkChange: (park: Park) => void;
  loading?: boolean;
}

export default function ParkSelector({
  parks,
  selectedPark,
  onParkChange,
  loading = false,
}: ParkSelectorProps) {
  const [query, setQuery] = useState("");

  const filteredParks =
    query === ""
      ? parks
      : parks.filter(
          (park) =>
            park.name.toLowerCase().includes(query.toLowerCase()) ||
            park.park_id.toLowerCase().includes(query.toLowerCase()) ||
            park.state.toLowerCase().includes(query.toLowerCase())
        );

  if (loading) {
    return (
      <div className="w-full">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select National Park
        </label>
        <div className="animate-pulse bg-gray-200 h-10 rounded-md"></div>
      </div>
    );
  }

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Select National Park
      </label>

      <Listbox value={selectedPark} onChange={onParkChange}>
        <div className="relative">
          <ListboxButton className="relative w-full cursor-default rounded-md bg-white py-2 pl-3 pr-10 text-left shadow-sm border border-gray-300 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500 sm:text-sm">
            <span className="flex items-center">
              <MapPinIcon className="h-4 w-4 text-gray-400 mr-2 flex-shrink-0" />
              {selectedPark ? (
                <span className="block truncate">
                  <span className="font-medium">{selectedPark.name}</span>
                  <span className="text-gray-500 ml-2">
                    ({selectedPark.park_id})
                  </span>
                </span>
              ) : (
                <span className="block truncate text-gray-500">
                  Choose a park...
                </span>
              )}
            </span>
            <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <ChevronsUpDownIcon
                className="h-4 w-4 text-gray-400"
                aria-hidden="true"
              />
            </span>
          </ListboxButton>

          <Transition
            as={Fragment}
            leave="transition ease-in duration-100"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <ListboxOptions className="absolute z-10 mt-1 max-h-80 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
              <div className="sticky top-0 bg-white px-3 py-2 border-b border-gray-200 z-1">
                <input
                  type="text"
                  className="w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm placeholder-gray-500 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
                  placeholder="Search parks..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </div>

              {filteredParks.length === 0 && query !== "" ? (
                <div className="relative cursor-default select-none py-2 px-4 text-gray-700">
                  <span className="block truncate">No parks found.</span>
                </div>
              ) : (
                filteredParks.map((park) => (
                  <ListboxOption
                    key={park.park_id}
                    disabled={park.has_model ? false : true}
                    className={({ active }) =>
                      cn(
                        "relative cursor-default select-none py-2 pl-10 pr-4",
                        active
                          ? "bg-green-100 text-green-900"
                          : "text-gray-900",
                        park.has_model ? "" : "disabledParkItem"
                      )
                    }
                    value={park}
                  >
                    {({ selected }) => (
                      <>
                        <div className="flex items-center">
                          <div className="flex-1 min-w-0 parkItemInfo">
                            <span
                              className={cn(
                                "block truncate",
                                selected ? "font-medium" : "font-normal"
                              )}
                            >
                              {park.name}
                            </span>
                            <span className="text-xs text-gray-500 truncate">
                              {park.state} • {park.region} • {park.park_type}
                            </span>
                            {park.visitor_stats && (
                              <span className="text-xs text-gray-400 truncate">
                                Avg:{" "}
                                {park.visitor_stats.avg_visitors.toLocaleString()}{" "}
                                visitors/day
                              </span>
                            )}
                          </div>

                          <div className="flex items-center space-x-1 ml-2">
                            {park.has_model ? (
                              <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                ✓
                              </span>
                            ) : (
                              <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-600">
                                ✗
                              </span>
                            )}
                          </div>
                        </div>

                        {selected ? (
                          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-green-600">
                            <CheckIcon className="h-4 w-4" aria-hidden="true" />
                          </span>
                        ) : null}
                      </>
                    )}
                  </ListboxOption>
                ))
              )}
            </ListboxOptions>
          </Transition>
        </div>
      </Listbox>

      {selectedPark && (
        <div className="mt-2 p-3 bg-gray-50 rounded-md">
          <div className="selectedPark flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-900">
                {selectedPark.name}
              </p>
              <p className="text-xs text-gray-500">
                {selectedPark.state} • {selectedPark.region}
              </p>
            </div>
            <div className="text-right">
              {selectedPark.visitor_stats && (
                <div className="text-xs text-gray-600 visitorStats">
                  <div>
                    <span>Peak</span>
                    {selectedPark.visitor_stats.max_visitors.toLocaleString()}
                  </div>
                  <div>
                    <span>Average</span>
                    {selectedPark.visitor_stats.avg_visitors.toLocaleString()}
                  </div>
                  <div>
                    <span>Low</span>
                    {selectedPark.visitor_stats.min_visitors.toLocaleString()}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
