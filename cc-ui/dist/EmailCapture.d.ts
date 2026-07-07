import * as React from "react";
export interface EmailCaptureProps {
    /** Lead with the incentive, e.g. "10% off your first order" — never "join our newsletter". */
    heading: string;
    description?: string;
    buttonLabel?: string;
    onSubmit?: (email: string) => void;
}
/**
 * Pine-green email capture band with a brass submit button. The heading
 * carries a real incentive; the confirmation replaces vague promises with
 * a concrete next step.
 */
export declare function EmailCapture({ heading, description, buttonLabel, onSubmit }: EmailCaptureProps): React.JSX.Element;
