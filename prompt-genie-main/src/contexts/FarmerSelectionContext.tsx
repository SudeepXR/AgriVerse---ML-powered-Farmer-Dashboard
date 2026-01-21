    import React, { createContext, useContext, useState } from 'react';

    export type SelectedFarmer = {
    id: number;
    full_name?: string;
    village?: string;
    district?: string;
    };

    interface FarmerSelectionContextType {
    selectedFarmer: SelectedFarmer | null;
    setSelectedFarmer: (farmer: SelectedFarmer) => void;
    }

    const FarmerSelectionContext = createContext<FarmerSelectionContextType | undefined>(undefined);

    export const FarmerSelectionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [selectedFarmer, setSelectedFarmer] = useState<SelectedFarmer | null>(null);

    return (
        <FarmerSelectionContext.Provider value={{ selectedFarmer, setSelectedFarmer }}>
        {children}
        </FarmerSelectionContext.Provider>
    );
    };

    export const useSelectedFarmer = () => {
    const ctx = useContext(FarmerSelectionContext);
    if (!ctx) throw new Error("useSelectedFarmer must be used within FarmerSelectionProvider");
    return ctx;
    };
